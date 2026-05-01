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
from ..utils.logger import logger

class ReportingService:
    @staticmethod
    def generar_cierre_z(db: Session, efectivo_declarado: float = None) -> ReporteZ:
        """
        Consolida la jornada operativa: Calcula cierres de caja, purga stock perecedero
        y genera el reporte fiscal oficial.
        """
        hoy = datetime.now()
        hoy_str = hoy.strftime("%Y-%m-%d")

        # 1. Análisis de Ventas Netas
        pedidos_hoy = (
            db.query(Pedido)
            .filter(Pedido.estado != "ESPERANDO_PAGO")
            .filter(func.date(Pedido.fecha) == hoy_str)
            .all()
        )

        total_efectivo = sum(p.total for p in pedidos_hoy if p.metodo_pago == "EFECTIVO")
        total_tarjeta = sum(p.total for p in pedidos_hoy if p.metodo_pago != "EFECTIVO")
        total_ventas = total_efectivo + total_tarjeta

        # Métricas de Domicilio
        pedidos_domicilio = [p for p in pedidos_hoy if p.metodo_envio == "DOMICILIO"]
        count_domicilio = len(pedidos_domicilio)
        total_fees_domicilio = count_domicilio * 2.50
        total_ventas_domicilio = sum(p.total for p in pedidos_domicilio)

        diferencia = 0.0
        if efectivo_declarado is not None:
            diferencia = efectivo_declarado - total_efectivo

        # 2. Auditoría de Mermas y Rendimiento de Cocina
        perecederos = db.query(Categoria).filter(Categoria.nombre.in_(["Pollos Asados", "Guarniciones"])).all()
        cat_ids = [c.id for c in perecederos]

        productos = db.query(Producto).all()

        sobrantes_texto = ""
        pollos_vendidos = 0
        coste_total_mermas = 0.0

        for p in productos:
            # Cálculo de unidades vendidas (Pollos)
            if "Pollo" in p.nombre:
                ventas_p = (
                    db.query(func.sum(MovimientoStock.cantidad))
                    .filter(MovimientoStock.producto_id == p.id)
                    .filter(MovimientoStock.tipo == "VENTA")
                    .filter(func.date(MovimientoStock.fecha) == hoy_str)
                    .scalar() or 0
                )
                pollos_vendidos += abs(int(ventas_p))

            # Proceso de Merma Automática (Auto-Mermas fin de jornada)
            if p.categoria_id in cat_ids and p.stock_actual > 0:
                merma_qty = p.stock_actual
                coste_estimado = merma_qty * (p.precio * 0.40) # Valoración al 40% del PVP
                coste_total_mermas += coste_estimado

                sobrantes_texto += f"🗑 {p.nombre}: {merma_qty} uds. (-{coste_estimado:.2f}€)\n"

                # Registrar purga en historial de stock
                db.add(MovimientoStock(
                    id=str(uuid.uuid4()),
                    producto_id=p.id,
                    cantidad=-merma_qty,
                    tipo="SOBRANTE_DIA",
                    descripcion="Cierre Z: Purgado automático de perecederos",
                ))
                p.stock_actual = 0
            elif p.stock_actual > 0:
                sobrantes_texto += f"📦 {p.nombre}: {p.stock_actual} uds. en stock\n"

        # 3. Construcción del Reporte Ejecutivo
        msg = "🐔 *REPORTE CIERRE Z - ENTERPRISE* 🐔\n"
        msg += f"📅 Jornada: {hoy.strftime('%d/%m/%Y')}\n\n"
        msg += f"💰 Ventas Efectivo: {total_efectivo:.2f}€\n"
        if efectivo_declarado is not None:
            msg += f"📝 Declarado Caja: {efectivo_declarado:.2f}€\n"
            status_icon = "✅" if diferencia == 0 else ("🔴 FALTANTE" if diferencia < 0 else "🔵 SOBRANTE")
            msg += f"⚖️ Desajuste: {diferencia:.2f}€ {status_icon}\n"
        msg += f"💳 Ventas Tarjeta: {total_tarjeta:.2f}€\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"📊 *FACTURACIÓN TOTAL: {total_ventas:.2f}€*\n"
        msg += f"🛵 Domicilios: {count_domicilio} ({total_ventas_domicilio:.2f}€)\n"
        msg += f"🚚 Tasas Envío: {total_fees_domicilio:.2f}€\n\n"
        msg += f"🍗 Pollos Despachados: {pollos_vendidos}\n"
        if coste_total_mermas > 0:
            msg += f"🚨 Impacto Mermas: -{coste_total_mermas:.2f}€\n\n"
        msg += "📦 *INVENTARIO FINAL*:\n"
        msg += sobrantes_texto if sobrantes_texto else "Sin stock remanente."

        # 4. Persistencia en Base de Datos
        nuevo_reporte = ReporteZ(
            id=str(uuid.uuid4()),
            fecha=hoy,
            total_ventas=total_ventas,
            total_efectivo=total_efectivo,
            total_tarjeta=total_tarjeta,
            efectivo_declarado=efectivo_declarado,
            diferencia=diferencia,
            pollos_vendidos=pollos_vendidos,
            coste_mermas=coste_total_mermas,
            resumen_texto=msg,
        )
        db.add(nuevo_reporte)
        db.commit()

        # 5. Notificación Industrial
        ReportingService._notificar_whatsapp(msg)

        return nuevo_reporte

    @staticmethod
    def _notificar_whatsapp(mensaje: str):
        """Notificación vía WAHA a la gerencia."""
        try:
            if not settings.WAHA_URL or not settings.ADMIN_WHATSAPP:
                return
            
            url = f"{settings.WAHA_URL}/api/sendText"
            payload = {
                "chatId": settings.ADMIN_WHATSAPP,
                "text": mensaje,
                "session": "default",
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Fallo en notificación WhatsApp de cierre: {e}")

    @staticmethod
    def generar_pdf_z(reporte: ReporteZ) -> str:
        """Genera el documento PDF formal del Cierre Z."""
        filename = f"cierre_z_{reporte.fecha.strftime('%Y%m%d_%H%M')}.pdf"
        filepath = os.path.join("instance", filename)
        os.makedirs("instance", exist_ok=True)

        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "REPORTE DE CIERRE FISCAL (Z)")
        c.setFont("Helvetica", 10)
        
        y = 720
        for linea in reporte.resumen_texto.split("\n"):
            clean_line = linea.replace("*", "").replace("━━━━━━━━━━━━━━━━━━━━━━━━", "--------------------")
            c.drawString(100, y, clean_line)
            y -= 15
            if y < 50:
                c.showPage()
                y = 750
        
        c.save()
        return filepath
