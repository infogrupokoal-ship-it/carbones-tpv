import os
import requests
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from ..models import MovimientoStock, Producto, LogOperativo
from ..utils.logger import logger

def enviar_alerta_whatsapp(mensaje: str):
    """
    Despacha alertas críticas de inventario al canal de administración.
    """
    try:
        # Recuperar configuración de entorno con valores por defecto seguros
        waha_url = os.environ.get("WAHA_URL")
        chat_id = os.environ.get("ADMIN_WHATSAPP")
        
        if not waha_url or not chat_id:
            return

        requests.post(
            f"{waha_url}/api/sendText",
            json={"chatId": chat_id, "text": mensaje, "session": "default"},
            timeout=5,
        )
    except Exception as e:
        logger.error(f"Fallo en despacho de alerta WhatsApp: {e}")

def descontar_stock_pedido(
    db: Session,
    producto_id: str,
    cantidad: int,
    pedido_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Motor de Gestión de Existencias:
    1. Procesa deducciones jerárquicas (Hijos -> Padre).
    2. Ejecuta explosión de materiales (Recetas -> Ingredientes).
    3. Monitorea niveles críticos y dispara alertas preventivas.
    """
    prod = db.query(Producto).get(producto_id)
    if not prod:
        return

    # --- 1. Lógica de Stock Jerárquico (Pue: 1/4 Pollo resta 0.25 del Padre 'Pollo Entero') ---
    if prod.stock_base_id:
        parent = db.query(Producto).get(prod.stock_base_id)
        if parent and parent.stock_actual is not None:
            cantidad_a_restar = cantidad * prod.factor_stock
            parent.stock_actual -= cantidad_a_restar
            
            db.add(MovimientoStock(
                producto_id=parent.id,
                cantidad=-cantidad_a_restar,
                tipo="VENTA",
                descripcion=f"Venta Indirecta (Hijo: {prod.nombre})",
            ))

            # Alerta de Stock Crítico en Producto Base
            if parent.stock_minimo is not None and parent.stock_minimo > 0 and parent.stock_actual <= parent.stock_minimo:
                msg = f"🚨 *STOCK CRÍTICO*: {parent.nombre} en {parent.stock_actual} uds. ¡Reponer producción!"
                background_tasks.add_task(enviar_alerta_whatsapp, msg)
                db.add(LogOperativo(
                    nivel="CRITICAL",
                    modulo="INVENTARIO",
                    mensaje=f"Alerta de stock crítico: {parent.nombre} ({parent.stock_actual} uds)"
                ))
    else:
        # Venta Directa
        if prod.stock_actual is not None:
            prod.stock_actual -= cantidad
            db.add(MovimientoStock(
                producto_id=prod.id,
                cantidad=-cantidad,
                tipo="VENTA",
                descripcion=f"Venta Directa: {prod.nombre}",
            ))

            if prod.stock_minimo is not None and prod.stock_minimo > 0 and prod.stock_actual <= prod.stock_minimo:
                msg = f"🚨 *ALERTA STOCK*: {prod.nombre} bajo mínimos ({prod.stock_actual} uds)."
                background_tasks.add_task(enviar_alerta_whatsapp, msg)
                db.add(LogOperativo(
                    nivel="WARNING",
                    modulo="INVENTARIO",
                    mensaje=f"Aviso de stock bajo: {prod.nombre} ({prod.stock_actual} uds)"
                ))

    # --- 2. Explosión de Receta (Descuento de Materia Prima / Ingredientes) ---
    for item_receta in prod.receta_items:
        ing = item_receta.ingrediente
        if ing and getattr(ing, 'stock_actual', None) is not None:
            demanda_total = item_receta.cantidad_necesaria * cantidad
            ing.stock_actual -= demanda_total

            # Auditoría de consumo de materia prima
            db.add(MovimientoStock(
                producto_id=None,
                cantidad=-demanda_total,
                tipo="CONSUMO_RECETA",
                descripcion=f"Consumo por venta de {prod.nombre} (ID Pedido: {pedido_id[:8]})"
            ))

            # Alerta de Suministros
            if getattr(ing, 'stock_minimo', None) is not None and ing.stock_minimo > 0 and ing.stock_actual <= ing.stock_minimo:
                msg = f"🛒 *AVISO PROVEEDOR*: {ing.nombre} en niveles críticos ({ing.stock_actual} {ing.unidad_medida})."
                background_tasks.add_task(enviar_alerta_whatsapp, msg)
                db.add(LogOperativo(
                    nivel="WARNING",
                    modulo="MATERIA_PRIMA",
                    mensaje=f"Materia prima crítica: {ing.nombre} ({ing.stock_actual} {ing.unidad_medida})"
                ))

    # El commit se gestiona en el router para asegurar atomicidad de la transacción.
