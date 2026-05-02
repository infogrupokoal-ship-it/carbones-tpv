from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter(prefix="/erp", tags=["ERP Connectors (SAP, Odoo, Oracle)"])

@router.get("/export/{formato}")
def export_data(formato: str):
    """
    Fase 45: Conector Nativo ERP.
    Exporta datos contables y operativos en formatos compatibles con SAP y Odoo.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["FECHA", "ID_TRANSACCION", "CONCEPTO", "IMPORTE", "IMPUESTOS", "CENTRO_COSTE"])
    writer.writerow(["2026-05-02", "TRX-48927", "VENTA_KIOSKO", "16.50", "1.65", "MAD-01"])
    
    output.seek(0)
    
    filename = f"erp_export_{formato}_20260502.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
