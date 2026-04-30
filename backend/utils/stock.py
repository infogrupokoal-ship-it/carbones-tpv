import logging
import os

import requests
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from ..models import Ingrediente, MovimientoStock, Producto, Receta

logger = logging.getLogger("StockUtils")


def enviar_alerta_whatsapp(mensaje: str):
    """Envía una alerta de stock vía WhatsApp de forma asíncrona."""
    try:
        waha_url = os.environ.get("WAHA_URL", "http://127.0.0.1:3000/api/sendText")
        chat_id = os.environ.get("ADMIN_WHATSAPP", "34604864187@c.us")
        requests.post(
            waha_url,
            json={"chatId": chat_id, "text": mensaje, "session": "default"},
            timeout=5,
        )
    except Exception as e:
        logger.error(f"Error enviando alerta WhatsApp: {e}")


def descontar_stock_pedido(
    db: Session,
    producto_id: str,
    cantidad: int,
    pedido_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Gestiona el descuento de stock fraccional y de ingredientes.
    Activa alertas si se llega al stock mínimo.
    """
    prod = db.query(Producto).get(producto_id)
    if not prod:
        return

    # 1. Lógica de Stock Fraccional (Hijos que restan de un Padre común)
    if prod.stock_base_id:
        parent = db.query(Producto).get(prod.stock_base_id)
        if parent:
            cantidad_a_restar = cantidad * prod.factor_stock
            parent.stock_actual -= cantidad_a_restar
            db.add(
                MovimientoStock(
                    producto_id=parent.id,
                    cantidad=-cantidad_a_restar,
                    tipo="VENTA",
                    origen_id=pedido_id,
                    descripcion=f"Venta (Hijo: {prod.nombre})",
                )
            )

            if parent.stock_minimo > 0 and parent.stock_actual <= parent.stock_minimo:
                msg = f"🚨 *ALERTA STOCK* 🚨\n*{parent.nombre}* está en {parent.stock_actual}.\n¡Reponer!"
                background_tasks.add_task(enviar_alerta_whatsapp, msg)
    else:
        prod.stock_actual -= cantidad
        db.add(
            MovimientoStock(
                producto_id=prod.id,
                cantidad=-cantidad,
                tipo="VENTA",
                origen_id=pedido_id,
                descripcion="Venta Directa",
            )
        )

        if prod.stock_minimo > 0 and prod.stock_actual <= prod.stock_minimo:
            msg = f"🚨 *ALERTA STOCK* 🚨\n*{prod.nombre}* está en {prod.stock_actual}.\n¡Hacer pedido!"
            background_tasks.add_task(enviar_alerta_whatsapp, msg)

    # 2. Lógica de Recetas (Descuento de Materia Prima)
    recetas = db.query(Receta).filter(Receta.producto_id == prod.id).all()
    for receta in recetas:
        ing = db.query(Ingrediente).get(receta.ingrediente_id)
        if ing:
            cantidad_ing = receta.cantidad_necesaria * cantidad
            ing.stock_actual -= cantidad_ing

            if ing.stock_minimo > 0 and ing.stock_actual <= ing.stock_minimo:
                msg = f"🚨 *ALERTA INGREDIENTE* 🚨\n*{ing.nombre}* bajo mínimo: {ing.stock_actual} {ing.unidad_medida}."
                background_tasks.add_task(enviar_alerta_whatsapp, msg)
