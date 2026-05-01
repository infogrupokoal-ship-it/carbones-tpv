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
    categoria: str = Field(..., alias="categoria_nombre")
    categoria_id: Optional[str] = None
    descripcion: Optional[str] = None
    stock_actual: float
    imagen_url: Optional[str]
    alergenos: Optional[str] = "Ninguno"
    info_nutricional: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
        populate_by_name = True

class CategoriaOut(BaseModel):
    id: str
    nombre: str

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
    Obtiene el estado crítico del inventario de materia prima y suministros activos.
    """
    try:
        # Respetar Soft Deletes
        ingredientes = db.query(Ingrediente).filter(Ingrediente.is_active == True).all()
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
    Lista el catálogo de productos activos con su estado de stock actual y categoría.
    """
    prods = db.query(Producto).filter(Producto.is_active == True).all()
    out = []
    for p in prods:
        out.append(ProductoOut(
            id=p.id,
            nombre=p.nombre,
            precio=p.precio,
            categoria_nombre=p.categoria.nombre if p.categoria else "Sin Categoría",
            categoria_id=p.categoria_id,
            descripcion=p.descripcion,
            stock_actual=p.stock_actual,
            imagen_url=p.imagen_url,
            alergenos=p.alergenos,
            info_nutricional=p.info_nutricional,
            is_active=p.is_active
        ))
    return out

@router.get("/categorias", response_model=List[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    """
    Obtiene las categorías activas disponibles para el filtrado en el Kiosko.
    """
    from ..models import Categoria
    cats = db.query(Categoria).filter(Categoria.is_active == True).all()
    return cats

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

class MermaRequest(BaseModel):
    entidad_tipo: str = Field(..., pattern="^(PRODUCTO|INGREDIENTE)$")
    entidad_id: str
    cantidad: float = Field(..., gt=0)
    motivo: str = Field(..., pattern="^(CADUCIDAD|ROTURA|ERROR_COCINA|OTRO)$")
    usuario_id: Optional[str] = None # En el futuro, sacar del token JWT

@router.post("/merma", status_code=status.HTTP_201_CREATED)
def registrar_merma(req: MermaRequest, db: Session = Depends(get_db)):
    """
    Endpoint avanzado para gestión de desperdicios. 
    Registra la merma calculando su coste asociado para Business Intelligence.
    """
    try:
        from ..models import Merma
        
        coste_unitario_estimado = 0.0
        nombre_entidad = ""
        
        if req.entidad_tipo == "PRODUCTO":
            item = db.query(Producto).get(req.entidad_id)
            if not item: raise HTTPException(404, "Producto no encontrado")
            # Coste estimado basado en un % del precio o cálculo de ingredientes
            coste_unitario_estimado = item.precio * 0.35 
            item.stock_actual -= req.cantidad
            nombre_entidad = item.nombre
        else:
            item = db.query(Ingrediente).get(req.entidad_id)
            if not item: raise HTTPException(404, "Ingrediente no encontrado")
            # Fallback seguro para modelos que no tienen coste_unitario aún
            coste_unitario_estimado = getattr(item, "coste_unitario", 0.0)
            item.stock_actual -= req.cantidad
            nombre_entidad = item.nombre

        coste_total_merma = coste_unitario_estimado * req.cantidad

        # Registrar Merma Detallada
        nueva_merma = Merma(
            id=str(uuid.uuid4()),
            entidad_tipo=req.entidad_tipo,
            entidad_id=req.entidad_id,
            cantidad=req.cantidad,
            motivo=req.motivo,
            coste_estimado=coste_total_merma,
            usuario_id=req.usuario_id
        )
        db.add(nueva_merma)

        # Reflejar en Movimientos de Stock
        db.add(MovimientoStock(
            id=str(uuid.uuid4()),
            producto_id=req.entidad_id if req.entidad_tipo == "PRODUCTO" else None,
            cantidad=-req.cantidad,
            tipo="MERMA",
            descripcion=f"Merma registrada: {req.motivo}"
        ))

        db.commit()
        logger.warning(f"🚨 Merma Industrial Registrada: {req.cantidad}x {nombre_entidad} | Motivo: {req.motivo} | Coste: {coste_total_merma}€")
        
        return {
            "status": "success", 
            "message": f"Merma de {nombre_entidad} registrada.",
            "impacto_financiero": coste_total_merma
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registrando merma: {str(e)}")
        raise HTTPException(status_code=500, detail="Fallo en registro de merma")
