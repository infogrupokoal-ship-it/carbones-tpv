import json
import uuid
import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Cliente, HardwareCommand, ItemPedido, Pedido, Producto
from ..utils.stock import descontar_stock_pedido

router = APIRouter(prefix="/orders", tags=["Orders"])
router_legacy = APIRouter(prefix="/pedidos", tags=["Legacy Pedidos"])



# --- Esquemas Pydantic ---
class ItemCrear(BaseModel):
    producto_id: str
    cantidad: int
    notas: Optional[str] = None


class PedidoCrear(BaseModel):
    items: List[ItemCrear]
    origen: str = "QUIOSCO"
    estado_inicial: str = "ESPERANDO_PAGO"
    cubiertos_qty: int = 0
    notas_cliente: Optional[str] = None
    canjear_puntos: bool = False


# --- Rutas ---


@router.get("/", response_model=List[dict])
@router_legacy.get("/", response_model=List[dict])
def listar_pedidos(estado: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    """Lista los pedidos con soporte para filtrado por estado."""
    query = db.query(Pedido)
    if estado:
        query = query.filter(Pedido.estado == estado)
    
    pedidos = query.order_by(Pedido.fecha.desc()).limit(limit).all()
    return [p.__dict__ for p in pedidos]


@router.get("/today", response_model=List[dict])
def listar_pedidos_hoy(db: Session = Depends(get_db)):
    """Filtrado rápido de la jornada actual para monitoreo."""
    today = datetime.date.today()
    pedidos = db.query(Pedido).filter(func.date(Pedido.fecha) == today).all()
    return [p.__dict__ for p in pedidos]


@router.get("/{pedido_id}/items")
@router_legacy.get("/{pedido_id}/items")
def obtener_items_pedido(pedido_id: str, db: Session = Depends(get_db)):
    """Obtiene el desglose de productos de un pedido."""
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    out = []
    for it in pedido.items:
        prod = db.query(Producto).get(it.producto_id)
        out.append({
            "id": it.id,
            "producto_id": it.producto_id,
            "nombre": prod.nombre if prod else "Producto Desconocido",
            "cantidad": it.cantidad,
            "precio": it.precio_unitario
        })
    return out


@router.post("/", response_model=dict)
def crear_pedido(
    pedido: PedidoCrear,
    background_tasks: BackgroundTasks,
    cliente_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Crea un pedido profesional con desglose fiscal, lógica de fidelidad
    y gestión de inventario asíncrona.
    """
    try:
        # 1. Identificación de Cliente y Fidelidad
        telefono_asociado = None
        if "-" in pedido.origen:
            origen_base, telefono_asociado = pedido.origen.split("-", 1)
        else:
            origen_base = pedido.origen

        cliente = None
        descuento_fidelidad = 0.0

        if cliente_id:
            cliente = db.query(Cliente).get(cliente_id)
        elif telefono_asociado:
            cliente = (
                db.query(Cliente).filter(Cliente.telefono == telefono_asociado).first()
            )
            if not cliente:
                cliente = Cliente(
                    id=str(uuid.uuid4()),
                    telefono=telefono_asociado,
                    nivel_fidelidad="BRONCE",
                )
                db.add(cliente)
                db.flush()

        if cliente:
            if cliente.nivel_fidelidad == "PLATA":
                descuento_fidelidad = 0.05
            elif cliente.nivel_fidelidad == "ORO":
                descuento_fidelidad = 0.10

        # 2. Inicialización de Pedido
        nuevo_pedido = Pedido(
            id=str(uuid.uuid4()),
            numero_ticket=f"T-{(db.query(Pedido).count() % 100) + 1:02d}",
            origen=origen_base,
            estado=pedido.estado_inicial,
            cliente_id=cliente.id if cliente else None,
            cubiertos_qty=pedido.cubiertos_qty,
            notas_cliente=pedido.notas_cliente,
        )
        db.add(nuevo_pedido)
        db.flush()

        # 3. Procesamiento de Ítems
        total_bruto = 0.0
        total_iva_10 = 0.0
        total_iva_21 = 0.0

        # Cargo de cubiertos (IVA 10%)
        if pedido.cubiertos_qty > 0:
            coste_cubiertos = pedido.cubiertos_qty * 0.20
            total_bruto += coste_cubiertos
            total_iva_10 += coste_cubiertos

        for item in pedido.items:
            prod = db.query(Producto).get(item.producto_id)
            if not prod:
                continue

            # Notas de ítem -> Notas de pedido
            if item.notas:
                nota_it = f"- {item.cantidad}x {prod.nombre}: {item.notas}"
                nuevo_pedido.notas_cliente = (
                    (nuevo_pedido.notas_cliente + "\n" + nota_it)
                    if nuevo_pedido.notas_cliente
                    else nota_it
                )

            # Descuento de Stock (Modular y Asíncrono)
            descontar_stock_pedido(
                db, prod.id, item.cantidad, nuevo_pedido.id, background_tasks
            )

            # Cálculo contable
            coste_it = prod.precio * item.cantidad
            total_bruto += coste_it

            if prod.impuesto == 21.0:
                total_iva_21 += coste_it
            else:
                total_iva_10 += coste_it

            db.add(
                ItemPedido(
                    id=str(uuid.uuid4()),
                    pedido_id=nuevo_pedido.id,
                    producto_id=prod.id,
                    cantidad=item.cantidad,
                    precio_unitario=prod.precio,
                )
            )

        # 4. Aplicación de Descuentos y Puntos
        total_final = total_bruto

        # Descuento por nivel
        if descuento_fidelidad > 0:
            total_final -= total_bruto * descuento_fidelidad
            total_iva_10 *= 1 - descuento_fidelidad
            total_iva_21 *= 1 - descuento_fidelidad

        # Canjeo de puntos (Pollos-Coins)
        if pedido.canjear_puntos and cliente and cliente.puntos_fidelidad >= 50:
            desc_puntos = (cliente.puntos_fidelidad // 50) * 5.0
            if desc_puntos > total_final:
                desc_puntos = total_final

            total_final -= desc_puntos
            cliente.puntos_fidelidad -= int((desc_puntos / 5.0) * 50)

            # Ajuste de IVA proporcional
            if total_bruto > 0:
                prop = desc_puntos / total_bruto
                total_iva_10 -= total_iva_10 * prop
                total_iva_21 -= total_iva_21 * prop

        # 5. Cierre Fiscal
        nuevo_pedido.total = round(total_final, 2)
        nuevo_pedido.descuento_aplicado = round(total_bruto - total_final, 2)

        nuevo_pedido.base_imponible_10 = round(total_iva_10 / 1.10, 2)
        nuevo_pedido.cuota_iva_10 = round(
            total_iva_10 - nuevo_pedido.base_imponible_10, 2
        )
        nuevo_pedido.base_imponible_21 = round(total_iva_21 / 1.21, 2)
        nuevo_pedido.cuota_iva_21 = round(
            total_iva_21 - nuevo_pedido.base_imponible_21, 2
        )

        # Acumulación de puntos
        if cliente:
            cliente.puntos_fidelidad += int(total_final)
            cliente.visitas += 1

        # 6. Comandos de Hardware (Si se paga/confirma al instante)
        if nuevo_pedido.estado == "EN_PREPARACION":
            _encolar_tickets(db, nuevo_pedido)

        db.commit()
        return {
            "status": "ok",
            "pedido_id": nuevo_pedido.id,
            "ticket": nuevo_pedido.numero_ticket,
            "total": nuevo_pedido.total,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{pedido_id}/estado")
@router_legacy.post("/{pedido_id}/estado")  # Legacy usa POST con query param
def actualizar_estado(pedido_id: str, estado: str, db: Session = Depends(get_db)):
    """Actualiza el estado de un pedido y dispara impresión si es necesario."""
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    estado_anterior = pedido.estado
    pedido.estado = estado

    # Si pasa a EN_PREPARACION desde ESPERANDO_PAGO, imprimimos
    if estado == "EN_PREPARACION" and estado_anterior == "ESPERANDO_PAGO":
        _encolar_tickets(db, pedido)

    db.commit()
    return {"status": "ok", "nuevo_estado": estado}


@router.post("/{pedido_id}/cobrar")
@router_legacy.post("/{pedido_id}/cobrar")
def cobrar_pedido(pedido_id: str, payload: dict, db: Session = Depends(get_db)):
    """Procesa el cobro, abre el cajón e imprime los tickets."""
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    metodo = payload.get("metodo_pago", "EFECTIVO")
    pedido.estado = "EN_PREPARACION"
    pedido.metodo_pago = metodo
    
    # 1. Encolar apertura de cajón si es efectivo
    if metodo == "EFECTIVO":
        db.add(HardwareCommand(
            id=str(uuid.uuid4()),
            accion="abrir_caja",
            origen="tpv_cobro"
        ))
    
    # 2. Encolar tickets (Cocina y Cliente)
    _encolar_tickets(db, pedido)
    
    db.commit()
    return {"status": "ok", "msj": "Cobro procesado correctamente."}


def _encolar_tickets(db: Session, pedido: Pedido):
    """Genera comandos de impresión para cocina y cliente."""
    items_payload = []
    for it in pedido.items:
        prod = db.query(Producto).get(it.producto_id)
        items_payload.append(
            {
                "nombre": prod.nombre if prod else "Item",
                "cantidad": it.cantidad,
                "precio": it.precio_unitario * it.cantidad,
            }
        )

    base_payload = {
        "numero_ticket": pedido.numero_ticket,
        "origen": pedido.origen,
        "total": pedido.total,
        "items": items_payload,
        "base_imponible_10": pedido.base_imponible_10,
        "cuota_iva_10": pedido.cuota_iva_10,
        "base_imponible_21": pedido.base_imponible_21,
        "cuota_iva_21": pedido.cuota_iva_21,
        "notas_cliente": pedido.notas_cliente,
    }

    # Ticket Cocina
    db.add(
        HardwareCommand(
            id=str(uuid.uuid4()),
            accion="imprimir",
            origen="backend_modular",
            payload=json.dumps({**base_payload, "tipo": "cocina"}),
        )
    )
    # Ticket Cliente
    db.add(
        HardwareCommand(
            id=str(uuid.uuid4()),
            accion="imprimir",
            origen="backend_modular",
            payload=json.dumps({**base_payload, "tipo": "cliente"}),
        )
    )

@router.post("/{pedido_id}/ubicacion")
def actualizar_ubicacion(pedido_id: str, payload: dict, db: Session = Depends(get_db)):
    """Actualiza la telemetría GPS de un pedido en tránsito."""
    # En una implementación avanzada, esto guardaría en una tabla de 'RutasGPS'
    from ..utils.db_logger import DBLogger
    lat = payload.get("lat")
    lon = payload.get("lon")
    dist = payload.get("distancia_metros")
    DBLogger.info("LOGISTICA", f"Pedido {pedido_id} a {dist}m (Lat: {lat}, Lon: {lon})")
    return {"status": "telemetry_received"}
