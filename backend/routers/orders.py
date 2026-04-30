import json
import uuid
import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Cliente, HardwareCommand, ItemPedido, Pedido, Producto
from ..utils.stock import descontar_stock_pedido
from ..utils.logger import logger

router = APIRouter(prefix="/orders", tags=["Operaciones"])
router_legacy = APIRouter(prefix="/pedidos", tags=["Legacy Pedidos"])

# --- Esquemas Pydantic ---

class ItemCrear(BaseModel):
    producto_id: str = Field(..., example="uuid-producto")
    cantidad: int = Field(..., gt=0, example=1)
    notas: Optional[str] = Field(None, example="Sin cebolla")

class PedidoCrear(BaseModel):
    items: List[ItemCrear]
    origen: str = Field("QUIOSCO", example="QUIOSCO")
    estado_inicial: str = Field("ESPERANDO_PAGO", example="ESPERANDO_PAGO")
    cubiertos_qty: int = Field(0, ge=0)
    notas_cliente: Optional[str] = None
    canjear_puntos: bool = False

class PedidoOut(BaseModel):
    id: str
    numero_ticket: str
    fecha: datetime.datetime
    estado: str
    total: float
    metodo_pago: Optional[str]
    origen: str
    
    class Config:
        from_attributes = True

class ItemPedidoOut(BaseModel):
    id: str
    producto_id: str
    nombre: str
    cantidad: int
    precio: float

# --- Rutas ---

@router.get("/", response_model=List[PedidoOut])
@router_legacy.get("/", response_model=List[PedidoOut])
def listar_pedidos(estado: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    """
    Lista los pedidos con soporte para filtrado por estado y paginación básica.
    """
    try:
        query = db.query(Pedido)
        if estado:
            query = query.filter(Pedido.estado == estado)
        
        pedidos = query.order_by(Pedido.fecha.desc()).limit(limit).all()
        return pedidos
    except Exception as e:
        logger.error(f"Error listando pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al listar pedidos")

@router.get("/today", response_model=List[PedidoOut])
def listar_pedidos_hoy(db: Session = Depends(get_db)):
    """
    Retorna todos los pedidos realizados en la fecha actual (Jornada Operativa).
    """
    today = datetime.date.today()
    pedidos = db.query(Pedido).filter(func.date(Pedido.fecha) == today).all()
    return pedidos

@router.get("/{pedido_id}/items", response_model=List[ItemPedidoOut])
@router_legacy.get("/{pedido_id}/items", response_model=List[ItemPedidoOut])
def obtener_items_pedido(pedido_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el desglose detallado de productos e importes de un pedido específico.
    """
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    out = []
    for it in pedido.items:
        prod = db.query(Producto).get(it.producto_id)
        out.append(ItemPedidoOut(
            id=it.id,
            producto_id=it.producto_id,
            nombre=prod.nombre if prod else "Producto Desconocido",
            cantidad=it.cantidad,
            precio=it.precio_unitario
        ))
    return out

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido: PedidoCrear,
    background_tasks: BackgroundTasks,
    cliente_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Crea un pedido profesional con desglose fiscal legal, lógica de fidelización 
    y gestión de inventario automatizada.
    """
    try:
        # 1. Gestión de Cliente y Fidelización
        telefono_asociado = None
        if "-" in pedido.origen:
            origen_parts = pedido.origen.split("-", 1)
            origen_base = origen_parts[0]
            telefono_asociado = origen_parts[1]
        else:
            origen_base = pedido.origen

        cliente = None
        descuento_fidelidad = 0.0

        if cliente_id:
            cliente = db.query(Cliente).get(cliente_id)
        elif telefono_asociado:
            cliente = db.query(Cliente).filter(Cliente.telefono == telefono_asociado).first()
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

        # 2. Creación del Pedido
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

        # 3. Procesamiento de Líneas de Pedido e Inventario
        total_bruto = 0.0
        total_iva_10 = 0.0
        total_iva_21 = 0.0

        # Cargo de cubiertos (IVA Reducido 10%)
        if pedido.cubiertos_qty > 0:
            coste_cubiertos = pedido.cubiertos_qty * 0.20
            total_bruto += coste_cubiertos
            total_iva_10 += coste_cubiertos

        for item in pedido.items:
            prod = db.query(Producto).get(item.producto_id)
            if not prod:
                logger.warning(f"Intento de añadir producto inexistente: {item.producto_id}")
                continue

            # Registro de notas por ítem en el pedido general
            if item.notas:
                nota_it = f"- {item.cantidad}x {prod.nombre}: {item.notas}"
                nuevo_pedido.notas_cliente = (
                    (nuevo_pedido.notas_cliente + "\n" + nota_it)
                    if nuevo_pedido.notas_cliente
                    else nota_it
                )

            # Deducción de Stock (Asíncrona para no bloquear la venta)
            descontar_stock_pedido(db, prod.id, item.cantidad, nuevo_pedido.id, background_tasks)

            # Cálculo Contable
            coste_it = prod.precio * item.cantidad
            total_bruto += coste_it

            if prod.impuesto == 21.0:
                total_iva_21 += coste_it
            else:
                total_iva_10 += coste_it

            db.add(ItemPedido(
                id=str(uuid.uuid4()),
                pedido_id=nuevo_pedido.id,
                producto_id=prod.id,
                cantidad=item.cantidad,
                precio_unitario=prod.precio,
            ))

        # 4. Aplicación de Descuentos
        total_final = total_bruto
        if descuento_fidelidad > 0:
            total_final -= total_bruto * descuento_fidelidad
            total_iva_10 *= (1 - descuento_fidelidad)
            total_iva_21 *= (1 - descuento_fidelidad)

        # 5. Cierre Fiscal y Contable
        nuevo_pedido.total = round(total_final, 2)
        nuevo_pedido.descuento_aplicado = round(total_bruto - total_final, 2)

        nuevo_pedido.base_imponible_10 = round(total_iva_10 / 1.10, 2)
        nuevo_pedido.cuota_iva_10 = round(total_iva_10 - nuevo_pedido.base_imponible_10, 2)
        nuevo_pedido.base_imponible_21 = round(total_iva_21 / 1.21, 2)
        nuevo_pedido.cuota_iva_21 = round(total_iva_21 - nuevo_pedido.base_imponible_21, 2)

        if cliente:
            cliente.puntos_fidelidad += int(total_final)
            cliente.visitas += 1

        # 6. Disparar impresión si el pedido ya está pagado/confirmado
        if nuevo_pedido.estado == "EN_PREPARACION":
            _encolar_tickets(db, nuevo_pedido)

        db.commit()
        logger.info(f"Pedido Creado: {nuevo_pedido.numero_ticket} | Total: {nuevo_pedido.total}€")
        
        return {
            "status": "success",
            "pedido_id": nuevo_pedido.id,
            "ticket": nuevo_pedido.numero_ticket,
            "total": nuevo_pedido.total,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error crítico creando pedido: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en el procesamiento del pedido")

@router.put("/{pedido_id}/estado")
@router_legacy.post("/{pedido_id}/estado")
def actualizar_estado(pedido_id: str, estado: str, db: Session = Depends(get_db)):
    """
    Cambia el flujo operativo de un pedido y dispara comandos de hardware (impresión) según el cambio.
    """
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    estado_anterior = pedido.estado
    pedido.estado = estado

    if estado == "EN_PREPARACION" and estado_anterior == "ESPERANDO_PAGO":
        _encolar_tickets(db, pedido)

    db.commit()
    return {"status": "success", "nuevo_estado": estado}

@router.post("/{pedido_id}/cobrar")
@router_legacy.post("/{pedido_id}/cobrar")
def cobrar_pedido(pedido_id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Finaliza el proceso de cobro, gestiona el cajón inteligente y emite tickets legales.
    """
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    metodo = payload.get("metodo_pago", "EFECTIVO")
    pedido.estado = "EN_PREPARACION"
    pedido.metodo_pago = metodo
    
    # 1. Seguridad Física: Abrir cajón si es pago manual
    if metodo == "EFECTIVO":
        db.add(HardwareCommand(
            id=str(uuid.uuid4()),
            accion="abrir_caja",
            origen="terminal_tpv_caja"
        ))
    
    # 2. Generación de Tickets
    _encolar_tickets(db, pedido)
    
    db.commit()
    logger.info(f"Cobro Procesado: Ticket {pedido.numero_ticket} mediante {metodo}")
    return {"status": "success", "message": "Operación de cobro completada"}

def _encolar_tickets(db: Session, pedido: Pedido):
    """
    Genera la carga útil de impresión profesional para Cocina y Cliente.
    """
    items_payload = []
    for it in pedido.items:
        prod = db.query(Producto).get(it.producto_id)
        items_payload.append({
            "nombre": prod.nombre if prod else "Item",
            "cantidad": it.cantidad,
            "precio": it.precio_unitario * it.cantidad,
        })

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
        "fecha": pedido.fecha.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Ticket Producción (Cocina)
    db.add(HardwareCommand(
        id=str(uuid.uuid4()),
        accion="imprimir",
        origen="backend_enterprise",
        payload=json.dumps({**base_payload, "tipo": "cocina"}),
    ))
    
    # Ticket Fiscal (Cliente)
    db.add(HardwareCommand(
        id=str(uuid.uuid4()),
        accion="imprimir",
        origen="backend_enterprise",
        payload=json.dumps({**base_payload, "tipo": "cliente"}),
    ))

@router.post("/{pedido_id}/ubicacion")
def actualizar_ubicacion(pedido_id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Recibe telemetría GPS para el seguimiento en vivo de entregas a domicilio.
    """
    lat = payload.get("lat")
    lon = payload.get("lon")
    dist = payload.get("distancia_metros")
    
    # Aquí podríamos actualizar Pedido.latitud_actual etc si quisiéramos persistencia GPS real
    logger.debug(f"Telemetría GPS: Pedido {pedido_id} a {dist}m")
    return {"status": "telemetry_accepted"}
