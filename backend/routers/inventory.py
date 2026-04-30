import uuid
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ingrediente, MovimientoStock, Producto
from ..utils.logger import logger

router = APIRouter(prefix="/inventory", tags=["Logística"])
router_legacy = APIRouter(prefix="/inventario", tags=["Legacy Inventario"])
router_productos = APIRouter(prefix="/productos", tags=["Catálogo"])

# --- Esquemas Pydantic ---

class IngredienteOut(BaseModel):
    id: str
    nombre: str
    stock_actual: float
    stock_minimo: float
    unidad: str = Field(..., alias="unidad_medida")
    proveedor_nombre: Optional[str] = "Sin Proveedor"
    proveedor_email: Optional[str] = ""

    class Config:
        from_attributes = True
        populate_by_name = True

class ProductoOut(BaseModel):
    id: str
    nombre: str
    precio: float
    categoria_id: Optional[str]
    stock_actual: float
    url_imagen: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class PedidoProveedorRequest(BaseModel):
    ingrediente_id: str
    cantidad: float = Field(..., gt=0)

class AjusteStockRequest(BaseModel):
    producto_id: Optional[str] = None
    ingrediente_id: Optional[str] = None
    cantidad: float
    tipo: str = Field("AJUSTE", pattern="^(AJUSTE|MERMA|REGALO|ENTRADA_PROVEEDOR)$")
    descripcion: Optional[str] = None

class ProduccionRequest(BaseModel):
    producto_id: str
    cantidad: float = Field(..., gt=0)
    descripcion: Optional[str] = "Producción manual en cocina"

# --- Rutas ---

@router.get("/ingredientes", response_model=List[IngredienteOut])
@router_legacy.get("/ingredientes", response_model=List[IngredienteOut])
def listar_ingredientes(db: Session = Depends(get_db)):
    """
    Obtiene el estado crítico del inventario de materia prima y suministros.
    """
    try:
        ingredientes = db.query(Ingrediente).all()
        out = []
        for ing in ingredientes:
            out.append(IngredienteOut(
                id=ing.id,
                nombre=ing.nombre,
                stock_actual=ing.stock_actual,
                stock_minimo=ing.stock_minimo,
                unidad_medida=ing.unidad_medida,
                proveedor_nombre=ing.proveedor.nombre if ing.proveedor else "Sin Proveedor",
                proveedor_email=ing.proveedor.email if ing.proveedor else ""
            ))
        return out
    except Exception as e:
        logger.error(f"Error listando ingredientes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al consultar inventario")

@router.get("/productos", response_model=List[ProductoOut])
@router_productos.get("/", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    """
    Lista el catálogo de productos activos con su estado de stock actual.
    """
    prods = db.query(Producto).filter(Producto.is_active).all()
    return prods

@router.post("/produccion", status_code=status.HTTP_201_CREATED)
@router_legacy.post("/produccion")
def registrar_produccion(req: ProduccionRequest, db: Session = Depends(get_db)):
    """
    Registra el procesado de materia prima en productos finales (Ej: Cocción de pollos).
    """
    prod = db.query(Producto).get(req.producto_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    prod.stock_actual += req.cantidad
    
    mov = MovimientoStock(
        id=str(uuid.uuid4()),
        producto_id=prod.id,
        cantidad=req.cantidad,
        tipo="PRODUCCION",
        descripcion=req.descripcion
    )
    db.add(mov)
    
    try:
        db.commit()
        logger.info(f"Producción registrada: {req.cantidad} unidades de {prod.nombre}")
        return {"status": "success", "message": f"Stock de {prod.nombre} actualizado (+{req.cantidad})"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro de producción: {str(e)}")
        raise HTTPException(status_code=500, detail="No se pudo registrar la producción")

@router.post("/pedido_proveedor", status_code=status.HTTP_201_CREATED)
def realizar_pedido_proveedor(req: PedidoProveedorRequest, db: Session = Depends(get_db)):
    """
    Simula la reposición de suministros tras una orden de compra a proveedores.
    """
    ing = db.query(Ingrediente).get(req.ingrediente_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

    prov = ing.proveedor
    logger.info(f"ORDEN COMPRA: {req.cantidad} {ing.unidad_medida} de {ing.nombre} -> {prov.nombre if prov else 'N/A'}")

    ing.stock_actual += req.cantidad
    db.add(MovimientoStock(
        id=str(uuid.uuid4()),
        producto_id=None,
        cantidad=req.cantidad,
        tipo="ENTRADA_PROVEEDOR",
        descripcion=f"Pedido a {prov.nombre if prov else 'proveedor'}",
    ))

    try:
        db.commit()
        return {"status": "success", "message": "Stock de materia prima repuesto"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error procesando entrada de mercancía")

@router.post("/ajuste", status_code=status.HTTP_200_OK)
def ajustar_stock(req: AjusteStockRequest, db: Session = Depends(get_db)):
    """
    Gestiona ajustes manuales, mermas por rotura o regalos de cortesía en el inventario.
    """
    try:
        target_name = ""
        if req.producto_id:
            item = db.query(Producto).get(req.producto_id)
            if not item: raise HTTPException(404, "Producto no encontrado")
            item.stock_actual += req.cantidad
            target_name = item.nombre
        elif req.ingrediente_id:
            item = db.query(Ingrediente).get(req.ingrediente_id)
            if not item: raise HTTPException(404, "Ingrediente no encontrado")
            item.stock_actual += req.cantidad
            target_name = item.nombre
        else:
            raise HTTPException(status_code=400, detail="Debe especificar un ID válido")

        db.add(MovimientoStock(
            id=str(uuid.uuid4()),
            producto_id=req.producto_id,
            cantidad=req.cantidad,
            tipo=req.tipo,
            descripcion=req.descripcion or f"Ajuste manual de {req.tipo.lower()}",
        ))

        db.commit()
        logger.warning(f"Ajuste de Stock [{req.tipo}]: {target_name} | Cambio: {req.cantidad}")
        return {"status": "success", "target": target_name}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error en ajuste de stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno en ajuste de inventario")
