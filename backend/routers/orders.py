import json
import uuid
import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Cliente, HardwareCommand, ItemPedido, Pedido, Producto, PrintJob, Usuario
from ..utils.stock import descontar_stock_pedido
from ..utils.logger import logger
from .admin_audit import log_audit_action
from .ws import notify_new_order
from .dependencies import get_current_user, require_admin, require_manager

router = APIRouter(prefix="/orders", tags=["Operaciones"])
router_legacy = APIRouter(prefix="/pedidos", tags=["Legacy Pedidos"])

# --- Esquemas Pydantic ---

class ItemCrear(BaseModel):
    producto_id: str = Field(..., json_schema_extra={"example": "uuid-producto"})
    cantidad: int = Field(..., gt=0, json_schema_extra={"example": 1})
    notas: Optional[str] = Field(None, json_schema_extra={"example": "Sin cebolla"})

class PedidoCrear(BaseModel):
    items: List[ItemCrear]
    origen: str = Field("QUIOSCO", json_schema_extra={"example": "QUIOSCO"})
    estado_inicial: str = Field("ESPERANDO_PAGO", json_schema_extra={"example": "ESPERANDO_PAGO"})
    cubiertos_qty: int = Field(0, ge=0)
    notas_cliente: Optional[str] = None
    canjear_puntos: bool = False
    cliente_id: Optional[str] = None
    metodo_envio: str = Field("LOCAL", json_schema_extra={"example": "LOCAL"})
    direccion: Optional[str] = None
    metodo_pago: str = Field("TARJETA", json_schema_extra={"example": "TARJETA"})

class ItemPedidoOut(BaseModel):
    id: str
    producto_id: Optional[str] = None
    nombre: str
    cantidad: int
    precio: float
    
    model_config = ConfigDict(from_attributes=True)

class PedidoOut(BaseModel):
    id: str
    numero_ticket: str
    fecha: datetime.datetime
    estado: str
    total: float
    metodo_pago: Optional[str]
    origen: str
    metodo_envio: Optional[str] = "LOCAL"
    direccion: Optional[str] = None
    notas_cliente: Optional[str] = None
    cliente_nombre: Optional[str] = "Anónimo"
    cliente_telefono: Optional[str] = None
    items: List[ItemPedidoOut] = [] # Incluimos items para el listado de caja
    
    model_config = ConfigDict(from_attributes=True)

# --- Rutas ---

@router.get("/", response_model=List[PedidoOut])
@router_legacy.get("/", response_model=List[PedidoOut])
def listar_pedidos(estado: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db), current_user: Usuario = Depends(require_manager)):
    """
    Lista los pedidos con soporte para filtrado por estado y paginación básica.
    """
    try:
        query = db.query(Pedido)
        if estado:
            query = query.filter(Pedido.estado == estado)
        
        return query.order_by(Pedido.fecha.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Error listando pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al listar pedidos")

@router.get("/pending", response_model=List[PedidoOut])
def listar_pedidos_pendientes(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """
    Endpoint optimizado para el KDS: Retorna pedidos en estado EN_PREPARACION.
    """
    try:
        return db.query(Pedido).filter(Pedido.estado == "EN_PREPARACION").order_by(Pedido.fecha.asc()).all()
    except Exception as e:
        logger.error(f"Error en /pending: {e}")
        return []

@router.get("/today", response_model=List[PedidoOut])
def listar_pedidos_hoy(db: Session = Depends(get_db), current_user: Usuario = Depends(require_manager)):
    """
    Retorna todos los pedidos realizados en la fecha actual (Jornada Operativa).
    """
    today = datetime.date.today()
    return db.query(Pedido).filter(func.date(Pedido.fecha) == today).all()

@router.get("/activas", response_model=List[PedidoOut])
@router.get("/active", response_model=List[PedidoOut])
def listar_pedidos_activos(db: Session = Depends(get_db)):
    """
    Retorna los pedidos que aún no están completados (para logística).
    """
    return db.query(Pedido).filter(Pedido.estado.in_(["ESPERANDO_PAGO", "EN_PREPARACION", "PREPARADO", "EN_CAMINO"])).all()

@router.get("/cierre-z")
def obtener_cierre_z(db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """
    Genera el Cierre Z de la jornada comercial actual.
    El corte se hace a las 04:00 UTC (06:00 ESP aprox) para que ventas de madrugada 
    se cuenten en la jornada comercial correcta, solucionando el problema de timezone.
    """
    now_utc = datetime.datetime.utcnow()
    
    # Si estamos antes de las 04:00 UTC, seguimos en la jornada comercial del día anterior
    if now_utc.hour < 4:
        jornada_date = (now_utc - datetime.timedelta(days=1)).date()
    else:
        jornada_date = now_utc.date()

    # Inicio a las 04:00:00 UTC del día que consideramos "Jornada"
    inicio_jornada = datetime.datetime.combine(jornada_date, datetime.time(4, 0, 0))
    fin_jornada = inicio_jornada + datetime.timedelta(days=1) - datetime.timedelta(microseconds=1)

    pedidos = db.query(Pedido).filter(
        Pedido.fecha >= inicio_jornada,
        Pedido.fecha <= fin_jornada,
        Pedido.estado == "COMPLETADO"
    ).all()
    
    total_dia = 0.0
    total_efectivo = 0.0
    total_tarjeta = 0.0
    pedidos_count = len(pedidos)

    for p in pedidos:
        total_dia += p.total
        if p.metodo_pago == "EFECTIVO":
            total_efectivo += p.total
        elif p.metodo_pago == "TARJETA":
            total_tarjeta += p.total

    return {
        "fecha": str(jornada_date),
        "pedidos_completados": pedidos_count,
        "total_ingresos": round(total_dia, 2),
        "desglose": {
            "EFECTIVO": round(total_efectivo, 2),
            "TARJETA": round(total_tarjeta, 2)
        }
    }
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
async def crear_pedido(
    pedido: PedidoCrear,
    background_tasks: BackgroundTasks,
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

        if pedido.cliente_id:
            cliente = db.query(Cliente).get(pedido.cliente_id)
        elif telefono_asociado:
            cliente = db.query(Cliente).filter(Cliente.telefono == telefono_asociado).first()
            if not cliente:
                cliente = Cliente(
                    id=str(uuid.uuid4()),
                    nombre=f"Cliente {telefono_asociado[-4:]}",
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
            total=0.0,
            metodo_pago=pedido.metodo_pago,
            tienda_id=db.query(Producto).first().tienda_id if db.query(Producto).first() else None,
            metodo_envio=pedido.metodo_envio,
            direccion=pedido.direccion
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

        # Cargo por Domicilio (IVA 10%)
        if pedido.metodo_envio == 'DOMICILIO':
            coste_envio = 2.50
            total_bruto += coste_envio
            total_iva_10 += coste_envio

        for item in pedido.items:
            prod = db.query(Producto).get(item.producto_id)
            if not prod:
                logger.warning(f"Producto inexistente ({item.producto_id}). Usando genérico.")
                # Fallback genérico para cross-selling sin ID real
                prod = Producto(id="0000", nombre="Varios/Genérico", precio=item.precio if hasattr(item, 'precio') else 0.0, impuesto=10.0, tienda_id=nuevo_pedido.tienda_id)
                # No hacemos db.add(prod) para no ensuciar el catálogo, solo lo usamos para el cálculo
            
            # --- VALIDACIÓN SÍNCRONA DE STOCK ---
            if prod.id != "0000" and getattr(prod, 'stock_actual', None) is not None:
                if prod.stock_actual < item.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para '{prod.nombre}'. Solicitado: {item.cantidad}, Disponible: {prod.stock_actual}."
                    )

            # Registro de notas por ítem en el pedido general
            if item.notas:
                nota_it = f"- {item.cantidad}x {prod.nombre}: {item.notas}"
                nuevo_pedido.notas_cliente = (
                    (nuevo_pedido.notas_cliente + "\n" + nota_it)
                    if nuevo_pedido.notas_cliente
                    else nota_it
                )

            # Deducción de Stock (Asíncrona para no bloquear la venta)
            if prod.id != "0000":
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
                producto_id=item.producto_id if prod.id != "0000" else None,
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
            cliente.puntos_fidelidad += int(total_final * 10)
            cliente.visitas += 1
            
            # Autopromoción de Nivel CRM
            if cliente.puntos_fidelidad >= 1500 and cliente.nivel_fidelidad != "ORO":
                cliente.nivel_fidelidad = "ORO"
                logger.info(f"🏆 Cliente {cliente.telefono} promovido a nivel ORO!")
            elif cliente.puntos_fidelidad >= 500 and cliente.puntos_fidelidad < 1500 and cliente.nivel_fidelidad == "BRONCE":
                cliente.nivel_fidelidad = "PLATA"
                logger.info(f"⭐ Cliente {cliente.telefono} promovido a nivel PLATA!")

        # 6. Disparar impresión si el pedido ya está pagado/confirmado
        if nuevo_pedido.estado == "EN_PREPARACION":
            _encolar_tickets(db, nuevo_pedido)

        db.commit()
        
        # Auditoría de Creación
        log_audit_action(
            db=db,
            usuario_id=pedido.cliente_id if hasattr(pedido, 'cliente_id') else None,
            accion="CREAR_PEDIDO",
            entidad="PEDIDO",
            entidad_id=nuevo_pedido.id,
            payload_nuevo=f"Ticket: {nuevo_pedido.numero_ticket} | Total: {nuevo_pedido.total}€"
        )

        logger.info(f"Pedido Creado: {nuevo_pedido.numero_ticket} | Total: {nuevo_pedido.total}€")
        
        # Notificar al KDS en tiempo real
        ws_payload = {
            "id": nuevo_pedido.id,
            "ticket": nuevo_pedido.numero_ticket,
            "estado": nuevo_pedido.estado,
            "total": nuevo_pedido.total,
            "origen": nuevo_pedido.origen
        }
        background_tasks.add_task(notify_new_order, ws_payload)
        
        response_data = {
            "status": "success",
            "pedido_id": nuevo_pedido.id,
            "ticket": nuevo_pedido.numero_ticket,
            "total": nuevo_pedido.total,
            "estado": nuevo_pedido.estado,
            "metodo_pago": nuevo_pedido.metodo_pago,
        }

        # Integración con Stripe para pagos online
        if pedido.metodo_pago == "TARJETA" and "QUIOSCO" in pedido.origen:
            from ..services.stripe_gateway import StripeGateway
            stripe_gw = StripeGateway()
            # Stripe session URL
            session_url = await stripe_gw.crear_checkout_session(nuevo_pedido.id, nuevo_pedido.total)
            if session_url:
                response_data["stripe_url"] = session_url
                logger.info(f"Stripe Checkout generado para pedido {nuevo_pedido.id}")

        return response_data

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error crítico creando pedido: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en el procesamiento del pedido")

@router.put("/{pedido_id}/estado")
@router_legacy.post("/{pedido_id}/estado")
def actualizar_estado(pedido_id: str, estado: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
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

    # Lógica Logística / Repartidores
    if estado == "EN_CAMINO" and estado_anterior != "EN_CAMINO":
        from ..models import AsignacionReparto, Usuario
        repartidor = db.query(Usuario).filter(Usuario.rol == "REPARTIDOR", Usuario.is_active).first()
        if repartidor:
            asignacion = AsignacionReparto(
                id=str(uuid.uuid4()),
                pedido_id=pedido.id,
                repartidor_id=repartidor.id,
                estado="EN_CAMINO"
            )
            db.add(asignacion)
            logger.info(f"Pedido {pedido.numero_ticket} asignado a repartidor {repartidor.username}")

    if estado == "ENTREGADO":
        from ..models import AsignacionReparto
        asignacion = db.query(AsignacionReparto).filter(AsignacionReparto.pedido_id == pedido.id).first()
        if asignacion:
            asignacion.estado = "ENTREGADO"
            asignacion.fecha_entrega = datetime.datetime.now(datetime.timezone.utc)

    db.commit()

    # Auditoría de Cambio de Estado
    log_audit_action(
        db=db,
        usuario_id=None,
        accion="ACTUALIZAR_ESTADO_PEDIDO",
        entidad="PEDIDO",
        entidad_id=pedido.id,
        payload_previo=estado_anterior,
        payload_nuevo=estado
    )
    
    # Notificar al KDS en tiempo real
    ws_payload = {
        "id": pedido.id,
        "ticket": pedido.numero_ticket,
        "estado": pedido.estado
    }
    background_tasks.add_task(notify_new_order, ws_payload)
    
    return {
        "status": "success",
        "nuevo_estado": estado,
        "estado": estado,
        "pedido_id": pedido.id,
        "ticket": pedido.numero_ticket,
        "total": pedido.total
    }

class UbicacionPayload(BaseModel):
    lat: float
    lon: float
    distancia_metros: int

@router.post("/{pedido_id}/ubicacion")
def actualizar_ubicacion(pedido_id: str, payload: UbicacionPayload, db: Session = Depends(get_db)):
    """
    Endpoint para recibir la telemetría GPS del cliente (Tracking).
    Ignora la posición si el pedido_id no existe, sin romper la aplicación.
    """
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        # En vez de 404 estricto, respondemos 200 ok pero ignoramos
        # para que el frontend no de error en loop
        return {"status": "ignored", "detail": "Pedido no válido"}
        
    # En un sistema completo, aquí se actualizaría la posición del rider/cliente 
    # y la cocina recibiría un evento por WebSockets.
    logger.info(f"Tracking Pedido {pedido_id}: a {payload.distancia_metros} metros.")
    return {"status": "success", "distancia": payload.distancia_metros}


@router.post("/{pedido_id}/cobrar")
@router_legacy.post("/{pedido_id}/cobrar")
def cobrar_pedido(pedido_id: str, payload: Dict[str, Any], db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """
    Finaliza el proceso de cobro, gestiona el cajón inteligente y emite tickets legales.
    A través de la arquitectura de repositorios (OrderService).
    """
    from ..repositories.order_service import OrderService
    service = OrderService(db)
    metodo = payload.get("metodo_pago", "EFECTIVO")
    
    try:
        pedido = service.process_checkout(pedido_id, metodo)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Generación de Tickets
    _encolar_tickets(db, pedido)
    db.commit()
    
    # Auditoría de Cobro
    log_audit_action(
        db=db,
        usuario_id=None,
        accion="COBRAR_PEDIDO",
        entidad="PEDIDO",
        entidad_id=pedido_id,
        payload_nuevo=f"Metodo: {metodo} | Total: {pedido.total}€"
    )

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

    # Ticket Producción (Cocina) - Arquitectura Zero-Touch
    db.add(PrintJob(
        id=str(uuid.uuid4()),
        payload=json.dumps({**base_payload, "tipo": "cocina"}),
        target_device="KITCHEN_PRINTER_01",
        status="PENDING",
        metadata_json={"order_id": pedido.numero_ticket, "type": "KITCHEN"}
    ))
    
    # Ticket Fiscal (Cliente) - Arquitectura Zero-Touch
    db.add(PrintJob(
        id=str(uuid.uuid4()),
        payload=json.dumps({**base_payload, "tipo": "cliente"}),
        target_device="TPV_FRONT_PRINTER",
        status="PENDING",
        metadata_json={"order_id": pedido.numero_ticket, "type": "CUSTOMER"}
    ))

