from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Pedido
from pydantic import BaseModel
import datetime

router = APIRouter(prefix="/logistics", tags=["Logística y Riders"])

class AsignacionRequest(BaseModel):
    pedido_id: str
    repartidor_nombre: str

class EstadoRepartoRequest(BaseModel):
    pedido_id: str
    nuevo_estado: str # EN_CAMINO, ENTREGADO, FALLIDO

@router.post("/assign")
def asignar_repartidor(req: AsignacionRequest, db: Session = Depends(get_db)):
    """Asigna un pedido a un repartidor específico."""
    pedido = db.query(Pedido).filter(Pedido.id == req.pedido_id).first()
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
        
    pedido.estado = "ASIGNADO_REPARTO"
    # En un entorno real tendríamos una tabla "Repartidor" y "Asignacion"
    # Para la fase 5.1 usamos notas u orígenes para marcar al repartidor
    pedido.notas = f"{pedido.notas or ''} | Repartidor: {req.repartidor_nombre}"
    
    db.commit()
    
    return {"status": "success", "message": f"Pedido {pedido.id} asignado a {req.repartidor_nombre}"}

@router.post("/update-status")
def actualizar_estado_reparto(req: EstadoRepartoRequest, db: Session = Depends(get_db)):
    """Actualiza el estado de entrega en tiempo real."""
    pedido = db.query(Pedido).filter(Pedido.id == req.pedido_id).first()
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
        
    pedido.estado = req.nuevo_estado
    db.commit()
    
    # Notificar via WebSocket a la oficina
    from backend.routers.ws import manager
    import asyncio
    asyncio.run(manager.broadcast({
        "type": "estado_reparto",
        "pedido_id": pedido.id,
        "nuevo_estado": req.nuevo_estado
    }))
    
    return {"status": "success", "message": "Estado logístico actualizado"}

@router.get("/commissions/{repartidor_nombre}")
def obtener_comisiones(repartidor_nombre: str, db: Session = Depends(get_db)):
    """Calcula las pre-nóminas (comisiones) del repartidor del día actual."""
    today = datetime.date.today()
    pedidos = db.query(Pedido).filter(
        func.date(Pedido.fecha) == today,
        Pedido.notas.like(f"%Repartidor: {repartidor_nombre}%"),
        Pedido.estado == "ENTREGADO"
    ).all()
    
    # Base: 2€ por entrega + 5% del total del pedido
    total_entregas = len(pedidos)
    comision_base = total_entregas * 2.0
    comision_variable = sum([p.total * 0.05 for p in pedidos])
    
    return {
        "repartidor": repartidor_nombre,
        "fecha": str(today),
        "entregas_exitosas": total_entregas,
        "comision_fija": round(comision_base, 2),
        "comision_variable": round(comision_variable, 2),
        "total_a_pagar": round(comision_base + comision_variable, 2)
    }
