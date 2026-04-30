import logging

logger = logging.getLogger(__name__)


def registrar_pedido_kiosko(db, cliente_id: int, items: list, origen: str = "WHATSAPP"):
    """
    Registra un pedido de comida en el sistema TPV.
    """
    from models import ItemPedido, MovimientoStock, Pedido, Producto

    nuevo_pedido = Pedido(
        numero_ticket=f"WPP-{cliente_id}-{db.query(Pedido).count() + 1}",
        origen=origen,
        estado="ESPERANDO_PAGO",
        cliente_id=cliente_id,
    )
    db.add(nuevo_pedido)
    db.flush()

    total = 0.0
    total_iva_10 = 0.0
    total_iva_21 = 0.0

    for it in items:
        prod_id = it.get("producto_id")
        cantidad = it.get("cantidad", 1)
        prod = db.query(Producto).get(prod_id)
        if prod:
            # Control stock
            if prod.stock_base_id:
                parent = db.query(Producto).get(prod.stock_base_id)
                if parent:
                    parent.stock_actual -= cantidad * prod.factor_stock
                    db.add(
                        MovimientoStock(
                            producto_id=parent.id,
                            cantidad=-(cantidad * prod.factor_stock),
                            tipo="VENTA",
                            origen_id=nuevo_pedido.id,
                            descripcion=f"Venta IA (Ref: {prod.nombre})",
                        )
                    )
            else:
                prod.stock_actual -= cantidad
                db.add(
                    MovimientoStock(
                        producto_id=prod.id,
                        cantidad=-cantidad,
                        tipo="VENTA",
                        origen_id=nuevo_pedido.id,
                        descripcion="Venta IA Automatica",
                    )
                )

            coste_item = prod.precio * cantidad
            total += coste_item

            if prod.impuesto == 21.0:
                total_iva_21 += coste_item
            else:
                total_iva_10 += coste_item

            db.add(
                ItemPedido(
                    pedido_id=nuevo_pedido.id,
                    producto_id=prod.id,
                    cantidad=cantidad,
                    precio_unitario=prod.precio,
                )
            )

    nuevo_pedido.total = round(total, 2)
    nuevo_pedido.base_imponible_10 = round(total_iva_10 / 1.10, 2)
    nuevo_pedido.cuota_iva_10 = round(total_iva_10 - nuevo_pedido.base_imponible_10, 2)
    nuevo_pedido.base_imponible_21 = round(total_iva_21 / 1.21, 2)
    nuevo_pedido.cuota_iva_21 = round(total_iva_21 - nuevo_pedido.base_imponible_21, 2)
    db.commit()
    return {"status": "ok", "ticket": nuevo_pedido.numero_ticket, "total": total}


def actualizar_stock_cocina(
    db,
    producto_id: int,
    cantidad_anadida: int,
    precio_nuevo: float = None,
    alergenos: str = None,
):
    """
    Permite al personal de cocina añadir stock producido y actualizar información técnica.
    """
    from models import MovimientoStock, Producto

    prod = db.query(Producto).get(producto_id)
    if not prod:
        return {"error": "El producto no existe."}

    prod.stock_actual += cantidad_anadida
    if precio_nuevo is not None:
        prod.precio = float(precio_nuevo)
    if alergenos is not None:
        prod.alergenos = alergenos

    db.add(
        MovimientoStock(
            producto_id=prod.id,
            cantidad=cantidad_anadida,
            tipo="PRODUCCION",
            descripcion=f"IA Cocina (+{cantidad_anadida})",
        )
    )
    db.commit()
    return {
        "status": "ok",
        "producto": prod.nombre,
        "stock_actualizado": prod.stock_actual,
    }
