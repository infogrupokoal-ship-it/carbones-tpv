import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ingrediente, MovimientoStock, Producto

router = APIRouter(prefix="/inventory", tags=["Inventory"])
router_legacy = APIRouter(prefix="/inventario", tags=["Legacy Inventario"])
router_productos = APIRouter(prefix="/productos", tags=["Productos"])



# --- Esquemas Pydantic ---
class IngredienteOut(BaseModel):
    id: str
    nombre: str
    stock_actual: float
    stock_minimo: float
    unidad: str
    proveedor_nombre: Optional[str]
    proveedor_email: Optional[str]

    class Config:
        orm_mode = True


class PedidoProveedorRequest(BaseModel):
    ingrediente_id: str
    cantidad: float


class AjusteStockRequest(BaseModel):
    producto_id: Optional[str] = None
    ingrediente_id: Optional[str] = None
    cantidad: float
    tipo: str = "AJUSTE"  # AJUSTE, MERMA, REGALO
    descripcion: Optional[str] = None


# --- Rutas ---


@router.get("/ingredientes", response_model=List[IngredienteOut])
@router_legacy.get("/ingredientes", response_model=List[IngredienteOut])
def listar_ingredientes(db: Session = Depends(get_db)):
    """Obtiene el estado actual del inventario de materia prima."""
    ingredientes = db.query(Ingrediente).all()
    out = []
    for ing in ingredientes:
        out.append(
            {
                "id": ing.id,
                "nombre": ing.nombre,
                "stock_actual": ing.stock_actual,
                "stock_minimo": ing.stock_minimo,
                "unidad": ing.unidad_medida,
                "proveedor_nombre": ing.proveedor.nombre
                if ing.proveedor
                else "Sin Proveedor",
                "proveedor_email": ing.proveedor.email if ing.proveedor else "",
            }
        )
    return out


@router.get("/productos")
@router_productos.get("/")
def listar_productos(db: Session = Depends(get_db)):
    """Lista productos para gestión de stock o venta."""
    prods = db.query(Producto).filter(Producto.is_active).all()
    # Profesionalizar la salida evitando __dict__
    return [{
        "id": p.id,
        "nombre": p.nombre,
        "precio": p.precio,
        "categoria": p.categoria,
        "stock_actual": p.stock_actual,
        "imagen_url": p.imagen_url,
        "is_active": p.is_active
    } for p in prods]


@router.post("/produccion")
@router_legacy.post("/produccion")
def registrar_produccion(req: dict, db: Session = Depends(get_db)):
    """Registra la cocción manual de productos (Ej: Pollos Asados)."""
    p_id = req.get("producto_id")
    cant = req.get("cantidad", 0)
    
    prod = db.query(Producto).get(p_id)
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    
    prod.stock_actual += cant
    
    db.add(MovimientoStock(
        id=str(uuid.uuid4()),
        producto_id=prod.id,
        cantidad=cant,
        tipo="PRODUCCION",
        descripcion=req.get("descripcion", "Producción manual en cocina")
    ))
    
    db.commit()
    return {"status": "ok", "msj": f"Stock de {prod.nombre} incrementado."}


@router.post("/pedido_proveedor")
def realizar_pedido_proveedor(
    req: PedidoProveedorRequest, db: Session = Depends(get_db)
):
    """Simula un pedido al proveedor y repone el stock localmente."""
    ing = db.query(Ingrediente).get(req.ingrediente_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

    prov = ing.proveedor
    # Aquí se podría integrar con un servicio de email/whatsapp real en el futuro
    print(
        f"-> [ORDEN COMPRA] Solicitando {req.cantidad} {ing.unidad_medida} de {ing.nombre} a {prov.nombre if prov else 'S/P'}"
    )

    ing.stock_actual += req.cantidad
    db.add(
        MovimientoStock(
            id=str(uuid.uuid4()),
            producto_id=None,  # Es un ingrediente, no un producto final
            cantidad=req.cantidad,
            tipo="ENTRADA_PROVEEDOR",
            descripcion=f"Pedido a {prov.nombre if prov else 'proveedor'}",
        )
    )

    db.commit()
    return {"status": "ok", "msj": f"Stock de {ing.nombre} actualizado."}


@router.post("/ajuste")
def ajustar_stock(req: AjusteStockRequest, db: Session = Depends(get_db)):
    """Permite realizar ajustes manuales o mermas en productos o ingredientes."""
    try:
        if req.producto_id:
            item = db.query(Producto).get(req.producto_id)
            if not item:
                raise HTTPException(404, "Producto no encontrado")
            item.stock_actual += req.cantidad
        elif req.ingrediente_id:
            item = db.query(Ingrediente).get(req.ingrediente_id)
            if not item:
                raise HTTPException(404, "Ingrediente no encontrado")
            item.stock_actual += req.cantidad
        else:
            raise HTTPException(400, "Debe especificar producto_id o ingrediente_id")

        db.add(
            MovimientoStock(
                id=str(uuid.uuid4()),
                producto_id=req.producto_id,
                cantidad=req.cantidad,
                tipo=req.tipo,
                descripcion=req.descripcion or f"Ajuste manual de {req.tipo.lower()}",
            )
        )

        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))
