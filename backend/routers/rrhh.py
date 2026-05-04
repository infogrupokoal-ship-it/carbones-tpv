from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
import uuid

from ..database import get_db
from ..models import Usuario, Fichaje, Liquidacion
from ..utils.auth import verify_password
from ..utils.logger import logger
from .dependencies import require_admin, require_manager

router = APIRouter(prefix="/rrhh", tags=["Recursos Humanos"])

class FichajeRequest(BaseModel):
    pin: str = Field(..., json_schema_extra={"example": "1234"})
    tipo: str = Field(..., json_schema_extra={"example": "ENTRADA"}) # ENTRADA, SALIDA, PAUSA

class FichajeOut(BaseModel):
    id: str
    usuario_nombre: str
    tipo: str
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)

@router.post("/fichar")
def registrar_fichaje(req: FichajeRequest, db: Session = Depends(get_db)):
    """
    Sistema de Control de Presencia: Registra entradas y salidas mediante PIN.
    Garantiza el cumplimiento normativo y facilita el cálculo de nóminas operativas.
    """
    # Buscamos el usuario por el hash del PIN (simplificado para el ejemplo con comparación directa si no hay hash complejo)
    # En un entorno real usaríamos verify_password
    usuario = db.query(Usuario).filter(Usuario.is_active).all()
    target_user = None
    
    
    for u in usuario:
        # Aquí asumimos que el pin_hash se verifica contra el pin enviado
        if verify_password(req.pin, u.pin_hash):
            target_user = u
            break
            
    if not target_user:
        logger.warning("Intento de fichaje fallido con PIN incorrecto.")
        raise HTTPException(status_code=401, detail="PIN incorrecto o usuario no activo")

    nuevo_fichaje = Fichaje(
        id=str(uuid.uuid4()),
        usuario_id=target_user.id,
        tipo=req.tipo.upper(),
        fecha=datetime.now(datetime.timezone.utc)
    )
    db.add(nuevo_fichaje)
    db.commit()
    
    logger.info(f"Fichaje registrado: {target_user.username} - {req.tipo}")
    return {
        "status": "success",
        "usuario": target_user.full_name or target_user.username,
        "tipo": req.tipo,
        "hora": nuevo_fichaje.fecha.strftime("%H:%M:%S")
    }

@router.get("/estado-plantilla")
def obtener_estado_plantilla(db: Session = Depends(get_db), current_user: Usuario = Depends(require_manager)):
    """
    Retorna la lista de empleados y su último estado de fichaje hoy.
    """
    today = datetime.now(datetime.timezone.utc).date()
    usuarios = db.query(Usuario).filter(Usuario.is_active).all()
    
    resultado = []
    for u in usuarios:
        ultimo = db.query(Fichaje).filter(Fichaje.usuario_id == u.id).order_by(Fichaje.fecha.desc()).first()
        resultado.append({
            "username": u.username,
            "full_name": u.full_name or u.username,
            "rol": u.rol,
            "ultima_hora": ultimo.fecha.strftime("%H:%M") if ultimo and ultimo.fecha.date() == today else None
        })
    return resultado



@router.post("/liquidaciones/calcular")
def calcular_liquidaciones(fecha_inicio: str, fecha_fin: str, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """
    Calcula la liquidación financiera de los empleados (Ej: Repartidores) 
    para un rango de fechas.
    """
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    
    # Ejemplo: Liquidar a repartidores según pedidos entregados
    usuarios = db.query(Usuario).filter(Usuario.is_active, Usuario.rol == "REPARTIDOR").all()
    
    resultados = []
    for u in usuarios:
        # En una DB completa buscaríamos en AsignacionReparto, aquí contamos pedidos entregados
        # asumiendo que un REPARTIDOR está asignado (simplificado: contar pedidos DOMICILIO completados en el turno del repartidor)
        # Para el Kiosko Enterprise, asignaremos un importe de 1€ por entrega.
        # Aquí mockeamos los pedidos asumiendo que el modelo final vincularía la AsignacionReparto.
        
        # Como añadimos AsignacionReparto en models.py, busquemos ahí:
        from ..models import AsignacionReparto
        asignaciones = db.query(AsignacionReparto).filter(
            AsignacionReparto.repartidor_id == u.id,
            AsignacionReparto.estado == "ENTREGADO",
            AsignacionReparto.fecha_entrega >= inicio,
            AsignacionReparto.fecha_entrega <= fin
        ).all()
        
        total_pedidos = len(asignaciones)
        comision_por_pedido = 1.50 # 1.50€ por pedido entregado
        
        nueva_liq = Liquidacion(
            id=str(uuid.uuid4()),
            usuario_id=u.id,
            fecha_inicio=inicio,
            fecha_fin=fin,
            total_pedidos=total_pedidos,
            monto_fijo=0.0,
            comisiones=total_pedidos * comision_por_pedido,
            total_pagar=total_pedidos * comision_por_pedido,
            estado="PENDIENTE"
        )
        db.add(nueva_liq)
        resultados.append({
            "usuario": u.full_name or u.username,
            "total_pedidos": total_pedidos,
            "total_pagar": nueva_liq.total_pagar
        })
        
        
    db.commit()
    return {"status": "success", "generadas": len(resultados), "detalles": resultados}

@router.get("/exportar-nominas")
def exportar_prenominas(db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    """
    Fase 11: Exportación de pre-nóminas (CSV).
    Exporta el listado de liquidaciones pendientes para su importación en software contable.
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv

    liquidaciones = db.query(Liquidacion).filter(Liquidacion.estado == "PENDIENTE").all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID_Liquidacion", "Usuario_ID", "Fecha_Inicio", "Fecha_Fin", "Total_Pedidos", "Monto_Fijo", "Comisiones", "Total_A_Pagar", "Estado"])
    
    for liq in liquidaciones:
        writer.writerow([
            liq.id, liq.usuario_id, liq.fecha_inicio.strftime("%Y-%m-%d"), 
            liq.fecha_fin.strftime("%Y-%m-%d"), liq.total_pedidos, 
            liq.monto_fijo, liq.comisiones, liq.total_pagar, liq.estado
        ])
    
    output.seek(0)
    
    # Enviar respuesta como archivo CSV
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prenominas.csv"}
    )

