import datetime
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Presupuesto, ItemPresupuesto, Producto, Referido, WhatsAppTemplate
from ..utils.logger import logger

router = APIRouter(prefix="/commercial", tags=["Gestión Comercial"])

# --- Esquemas ---

class ItemPresupuestoCrear(BaseModel):
    producto_id: str
    cantidad: int

class PresupuestoCrear(BaseModel):
    cliente_id: Optional[str] = None
    fecha_validez: Optional[datetime.datetime] = None
    notas: Optional[str] = None
    items: List[ItemPresupuestoCrear]

class ItemPresupuestoOut(BaseModel):
    id: str
    producto_id: str
    cantidad: int
    precio_unitario: float
    nombre: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = super().from_orm(obj)
        if obj.producto:
            data.nombre = obj.producto.nombre
        return data

class PresupuestoOut(BaseModel):
    id: str
    numero_presupuesto: str
    fecha: datetime.datetime
    fecha_validez: Optional[datetime.datetime]
    total: float
    estado: str
    notas: Optional[str]
    cliente_nombre: Optional[str] = "Anónimo"
    items: List[ItemPresupuestoOut]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = super().from_orm(obj)
        if obj.cliente:
            data.cliente_nombre = obj.cliente.nombre
        else:
            data.cliente_nombre = "Anónimo"
        
        # Mapear items manualmente para incluir el nombre del producto
        mapped_items = []
        for it in obj.items:
            item_out = ItemPresupuestoOut.from_orm(it)
            item_out.nombre = it.producto.nombre if it.producto else "Producto"
            mapped_items.append(item_out)
        data.items = mapped_items
        return data

# --- Rutas Presupuestos ---

@router.get("/quotes", response_model=List[PresupuestoOut])
def listar_presupuestos(db: Session = Depends(get_db)):
    try:
        quotes = db.query(Presupuesto).order_by(Presupuesto.fecha.desc()).all()
        # FastAPI se encarga del mapeo si usamos from_attributes=True y clases compatibles
        # Pero para el nombre del cliente/producto, el from_orm ayuda
        return [PresupuestoOut.from_orm(q) for q in quotes]
    except Exception as e:
        logger.error(f"Error listando presupuestos: {e}")
        return []

@router.post("/quotes", response_model=PresupuestoOut)
def crear_presupuesto(data: PresupuestoCrear, db: Session = Depends(get_db)):
    try:
        count = db.query(Presupuesto).count() + 1
        num = f"PRE-{datetime.datetime.now().year}-{count:04d}"
        
        nuevo = Presupuesto(
            id=str(uuid.uuid4()),
            numero_presupuesto=num,
            fecha=datetime.datetime.utcnow(),
            fecha_validez=data.fecha_validez or (datetime.datetime.utcnow() + datetime.timedelta(days=15)),
            total=0,
            estado="BORRADOR",
            notas=data.notas,
            cliente_id=data.cliente_id
        )
        
        db.add(nuevo)
        total = 0
        for item in data.items:
            prod = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if not prod:
                continue
            
            it = ItemPresupuesto(
                id=str(uuid.uuid4()),
                presupuesto_id=nuevo.id,
                producto_id=prod.id,
                cantidad=item.cantidad,
                precio_unitario=prod.precio
            )
            total += (prod.precio * item.cantidad)
            db.add(it)
            
        nuevo.total = total
        db.commit()
        db.refresh(nuevo)
        return PresupuestoOut.from_orm(nuevo)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando presupuesto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/quotes/{id}/status")
def actualizar_estado_presupuesto(id: str, estado: str, db: Session = Depends(get_db)):
    p = db.query(Presupuesto).filter(Presupuesto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    if estado == "ACEPTADO" and p.estado != "ACEPTADO":
        for item in p.items:
            if item.producto and hasattr(item.producto, 'stock') and item.producto.stock is not None:
                item.producto.stock -= item.cantidad
                
    p.estado = estado
    db.commit()
    return {"status": "ok", "nuevo_estado": estado}

# --- Rutas WhatsApp Templates ---

class WAPlateOut(BaseModel):
    id: str
    nombre: str
    slug: str
    contenido: str
    variables: str

    class Config:
        from_attributes = True

@router.get("/wa-templates", response_model=List[WAPlateOut])
def listar_plantillas(db: Session = Depends(get_db)):
    return db.query(WhatsAppTemplate).all()

# --- Rutas Referidos ---

class ReferidoOut(BaseModel):
    id: str
    fecha: datetime.datetime
    cliente_referidor_id: str
    cliente_referido_id: str
    estado: str
    bono_aplicado: float

    class Config:
        from_attributes = True

@router.get("/referrals", response_model=List[ReferidoOut])
def listar_referidos(db: Session = Depends(get_db)):
    return db.query(Referido).all()
