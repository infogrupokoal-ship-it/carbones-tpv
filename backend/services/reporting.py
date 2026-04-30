import logging
import os
import uuid
from datetime import datetime

import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import (
    Categoria,
    MovimientoStock,
    Pedido,
    Producto,
    ReporteZ,
)
from ..config import settings

logger = logging.getLogger("ReportingService")


class ReportingService:
    @staticmethod
    def generar_cierre_z(db: Session, efectivo_declarado: float = None):
        """
        Genera el reporte financiero del día, purga stock perecedero y envía notificaciones.
        """
        hoy = datetime.now()
        hoy_str = hoy.strftime("%Y-%m-%d")

        # 1. Ventas por método de pago
        pedidos_hoy = (
            db.query(Pedido)
            .filter(Pedido.estado != "ESPERANDO_PAGO")
            .filter(func.date(Pedido.fecha) == hoy_str)
            .all()
        )

        total_efectivo = sum(
            p.total for p in pedidos_hoy if p.metodo_pago == "EFECTIVO"
        )
        total_tarjeta = sum(p.total for p in pedidos_hoy if p.metodo_pago != "EFECTIVO")
        total_caja = total_efectivo + total_tarjeta

        diferencia_arqueo = 0.0
        if efectivo_declarado is not None:
            diferencia_arqueo = efectivo_declarado - total_efectivo

        # 2. Gestión de Mermas y Pollos Vendidos
        perecederos = (
            db.query(Categoria)
            .filter(Categoria.nombre.in_(["Pollos Asados", "Guarniciones"]))
            .all()
        )
        cat_ids = [c.id for c in perecederos]

        productos = db.query(Producto).filter(Producto.stock_base_id == None).all()

        sobrantes_texto = ""
        pollos_vendidos = 0
        coste_total_mermas = 0.0

        for p in productos:
            # Pollos vendidos (basado en movimientos de stock)
            if "Pollo" in p.nombre:
                ventas_p = (
                    db.query(func.sum(MovimientoStock.cantidad))
                    .filter(MovimientoStock.producto_id == p.id)
                    .filter(MovimientoStock.tipo == "VENTA")
                    .filter(func.date(MovimientoStock.fecha) == hoy_str)
                    .scalar()
                    or 0
                )
                pollos_vendidos += abs(int(ventas_p))

            # Merma automática
            if p.categoria_id in cat_ids and p.stock_actual > 0:
                merma_qty = p.stock_actual
                coste_estimado = merma_qty * (p.precio * 0.40)
                coste_total_mermas += coste_estimado

                sobrantes_texto += f"🗑 {p.nombre}: {merma_qty} uds. (-{coste_estimado:.2f}€)\n"

                # Registrar purga
                db.add(
                    MovimientoStock(
                        id=str(uuid.uuid4()),
                        producto_id=p.id,
                        cantidad=-merma_qty,
                        tipo="SOBRANTE_DIA",
                        descripcion="Vaciado automático fin de día",
                    )
                )
                p.stock_actual = 0
            elif p.stock_actual != 0 and p.categoria_id not in cat_ids:
                sobrantes_texto += f"📦 {p.nombre}: {p.stock_actual}\n"

        # 3. Formatear Mensaje
        msg = "🐔 *CIERRE Z - CARBONES Y POLLOS* 🐔\n"
        msg += f"📅 Fecha: {hoy.strftime('%d/%m/%Y')}\n\n"
        msg += f"💰 Efectivo Sistema: {total_efectivo:.2f} €\n"
        if efectivo_declarado is not None:
            msg += f"📝 Efectivo Declarado: {efectivo_declarado:.2f} €\n"
            simbolo = (
                "✅"
                if diferencia_arqueo == 0
                else ("🔴 FALTANTE" if diferencia_arqueo < 0 else "🔵 SOBRANTE")
            )
            msg += f"⚖️ Diferencia: {diferencia_arqueo:.2f} € {simbolo}\n"
        msg += f"💳 Tarjeta: {total_tarjeta:.2f} €\n"
        msg += "------------------------\n"
        msg += f"📊 *TOTAL CAJA: {total_caja:.2f} €*\n\n"
        msg += f"🍗 Pollos Vendidos: {pollos_vendidos}\n\n"
        if coste_total_mermas > 0:
            msg += f"🚨 *COSTE MERMAS: -{coste_total_mermas:.2f} €*\n\n"
        msg += "📦 *INVENTARIO FINAL*:\n"
        msg += sobrantes_texto if sobrantes_texto else "Sin sobrantes."

        # 4. Persistir Reporte
        nuevo_reporte = ReporteZ(
            id=str(uuid.uuid4()),
            fecha_cierre=hoy,
            total_efectivo=total_efectivo,
            total_tarjeta=total_tarjeta,
            total_caja=total_caja,
            efectivo_declarado=efectivo_declarado or 0.0,
            diferencia_arqueo=diferencia_arqueo,
            pollos_vendidos=pollos_vendidos,
            coste_mermas=coste_total_mermas,
            resumen_texto=msg,
        )
        db.add(nuevo_reporte)
        db.commit()

        # 5. Notificar vía WhatsApp (Opcional/Asíncrono recomendado)
        ReportingService._notificar_whatsapp(msg)

        return nuevo_reporte

    @staticmethod
    def _notificar_whatsapp(mensaje: str):
        """Envía el reporte a través del servicio WAHA."""
        try:
            url = f"{settings.WAHA_URL}/api/sendText"
            payload = {
                "chatId": settings.ADMIN_WHATSAPP,
                "text": mensaje,
                "session": "default",
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Error enviando WhatsApp de cierre: {e}")

    @staticmethod
    def generar_pdf_z(reporte: ReporteZ):
        """Genera un archivo PDF para el reporte."""
        filename = f"reporte_z_{reporte.fecha_cierre.strftime('%Y%m%d')}.pdf"
        filepath = os.path.join("instance", filename)
        os.makedirs("instance", exist_ok=True)

        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "CARBONES Y POLLOS - REPORTE Z")
        c.setFont("Helvetica", 12)
        
        y = 720
        for linea in reporte.resumen_texto.split("\n"):
            c.drawString(100, y, linea.replace("*", "")) # Quitamos negritas de markdown
            y -= 20
            if y < 100:
                c.showPage()
                y = 750
        
        c.save()
        return filepath
