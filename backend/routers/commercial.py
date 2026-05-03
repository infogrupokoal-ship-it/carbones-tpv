import datetime
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Presupuesto, ItemPresupuesto, Producto, Referido, WhatsAppTemplate, Pedido, ItemPedido
from ..utils.logger import logger

router = APIRouter(prefix="/commercial", tags=["Gestión Comercial"])

@router.post("/quotes/{id}/convert")
def convertir_a_pedido(id: str, db: Session = Depends(get_db)):
    """Convierte un presupuesto aceptado en un pedido real del TPV."""
    try:
        p = db.query(Presupuesto).filter(Presupuesto.id == id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
        
        if p.estado != "ACEPTADO":
            # Si no está aceptado, lo aceptamos primero
            p.estado = "ACEPTADO"
            
        # Crear Pedido
        count = db.query(Pedido).count() + 1
        num_ticket = f"TKT-CONV-{datetime.datetime.now().year}-{count:04d}"
        
        nuevo_pedido = Pedido(
            id=str(uuid.uuid4()),
            numero_ticket=num_ticket,
            fecha=datetime.datetime.now(datetime.timezone.utc),
            total=p.total,
            estado="PENDIENTE",
            origen="COMERCIAL",
            cliente_id=p.cliente_id,
            tienda_id=None # Se debería asignar una por defecto o la del usuario actual
        )
        
        db.add(nuevo_pedido)
        
        # Copiar Items
        for item in p.items:
            it = ItemPedido(
                id=str(uuid.uuid4()),
                pedido_id=nuevo_pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            db.add(it)
            
        p.estado = "CONVERTIDO"
        db.commit()
        
        return {"status": "ok", "pedido_id": nuevo_pedido.id, "numero_ticket": num_ticket}
    except Exception as e:
        db.rollback()
        logger.error(f"Error convirtiendo presupuesto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        data = super().model_validate(obj, *args, **kwargs)
        if hasattr(obj, 'producto') and obj.producto:
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

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        data = super().model_validate(obj, *args, **kwargs)
        if hasattr(obj, 'cliente') and obj.cliente:
            data.cliente_nombre = obj.cliente.nombre
        else:
            data.cliente_nombre = "Anónimo"
        
        # Mapear items manualmente para incluir el nombre del producto
        mapped_items = []
        for it in obj.items:
            item_out = ItemPresupuestoOut.model_validate(it)
            item_out.nombre = it.producto.nombre if hasattr(it, 'producto') and it.producto else "Producto"
            mapped_items.append(item_out)
        data.items = mapped_items
        return data

# --- Rutas Presupuestos ---

@router.get("/quotes", response_model=List[PresupuestoOut])
def listar_presupuestos(db: Session = Depends(get_db)):
    try:
        quotes = db.query(Presupuesto).order_by(Presupuesto.fecha.desc()).all()
        # FastAPI se encarga del mapeo si usamos from_attributes=True y clases compatibles
        # Pero para el nombre del cliente/producto, el model_validate ayuda
        return [PresupuestoOut.model_validate(q) for q in quotes]
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
            fecha=datetime.datetime.now(datetime.timezone.utc),
            fecha_validez=data.fecha_validez or (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=15)),
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
        return PresupuestoOut.model_validate(nuevo)
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

@router.get("/products")
def listar_productos(db: Session = Depends(get_db)):
    """Retorna el catálogo completo de productos para el Kiosko B2C."""
    try:
        from ..models import Producto
        prods = db.query(Producto).all()
        return [{
            "id": p.id,
            "nombre": p.nombre,
            "precio": p.precio,
            "categoria": p.categoria,
            "imagen": p.imagen_url if hasattr(p, 'imagen_url') else "/static/img/pollo_asado.png",
            "descripcion": p.descripcion if hasattr(p, 'descripcion') else "Receta artesanal al carbón"
        } for p in prods]
    except Exception as e:
        logger.error(f"Error listando productos Kiosko: {e}")
        return []

# --- Rutas WhatsApp Templates ---

class WAPlateOut(BaseModel):
    id: str
    nombre: str
    slug: str
    contenido: str
    variables: str

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

@router.get("/referrals", response_model=List[ReferidoOut])
def listar_referidos(db: Session = Depends(get_db)):
    return db.query(Referido).all()

@router.put("/referrals/{id}/approve")
def aprobar_referido(id: str, db: Session = Depends(get_db)):
    from ..models import Cliente
    ref = db.query(Referido).filter(Referido.id == id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Referido no encontrado")
    
    if ref.estado != "COMPLETADO":
        ref.estado = "COMPLETADO"
        ref.bono_aplicado = 5.0  # Bono de ejemplo por referido
        
        # Abonar saldo al cliente referidor si existe el campo
        referidor = db.query(Cliente).filter(Cliente.id == ref.cliente_referidor_id).first()
        if referidor and hasattr(referidor, 'saldo'):
            if referidor.saldo is None:
                referidor.saldo = 0.0
            referidor.saldo += ref.bono_aplicado
            
        db.commit()
    
    return {"status": "ok", "estado": ref.estado, "bono_aplicado": ref.bono_aplicado}
