import io
from datetime import datetime

class PDFGenerator:
    """
    Fase 28: Generador de Documentos Legales (Facturas, Albaranes, Reportes).
    Utiliza una arquitectura extensible para emitir PDFs profesionales con branding.
    """
    
    @staticmethod
    def generate_invoice_pdf(order_data: dict) -> bytes:
        # En producción se usaría ReportLab o WeasyPrint.
        # Aquí generamos un "buffer" que simula el PDF para la arquitectura ASGI.
        
        invoice_content = f"""
        =========================================
        CARBONES Y POLLOS LA GRANJA S.L.
        NIF: B-12345678
        FACTURA SIMPLIFICADA # {order_data.get('ticket', '0001')}
        =========================================
        Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Cliente: {order_data.get('cliente', 'Anónimo')}
        
        CONCEPTOS:
        -----------------------------------------
        {order_data.get('resumen_items', 'Consumo General')}
        
        TOTAL: {order_data.get('total', 0.0)} EUR
        (IVA Incluido)
        
        Gracias por su confianza. EXPERIENCIA GOURMET.
        =========================================
        """
        
        return invoice_content.encode('utf-8')
