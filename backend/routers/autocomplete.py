from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from ..database import get_db
from ..models import Cliente, Producto, Ingrediente, Proveedor, Usuario, Tienda
from .auth import get_current_user

router = APIRouter(prefix="/autocomplete")

@router.get("/clientes")
async def autocomplete_clientes(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Búsqueda transversal de clientes por nombre o teléfono."""
    results = db.query(Cliente).filter(
        or_(
            Cliente.nombre.ilike(f"%{q}%"),
            Cliente.telefono.ilike(f"%{q}%")
        )
    ).limit(10).all()
    
    return [{"id": c.id, "text": f"{c.nombre} ({c.telefono})", "nombre": c.nombre, "telefono": c.telefono} for c in results]

@router.get("/productos")
async def autocomplete_productos(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Búsqueda de productos por nombre."""
    results = db.query(Producto).filter(
        Producto.nombre.ilike(f"%{q}%"),
        Producto.is_active == True
    ).limit(10).all()
    
    return [{"id": p.id, "text": p.nombre, "precio": p.precio} for p in results]

@router.get("/ingredientes")
async def autocomplete_ingredientes(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Búsqueda de ingredientes (materias primas)."""
    results = db.query(Ingrediente).filter(
        Ingrediente.nombre.ilike(f"%{q}%"),
        Ingrediente.is_active == True
    ).limit(10).all()
    
    return [{"id": i.id, "text": i.nombre, "unidad": i.unidad_medida} for i in results]

@router.get("/proveedores")
async def autocomplete_proveedores(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Búsqueda de proveedores."""
    results = db.query(Proveedor).filter(
        Proveedor.nombre.ilike(f"%{q}%"),
        Proveedor.is_active == True
    ).limit(10).all()
    
    return [{"id": p.id, "text": p.nombre, "telefono": p.telefono} for p in results]

@router.get("/personal")
async def autocomplete_personal(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Búsqueda de personal (usuarios)."""
    results = db.query(Usuario).filter(
        or_(
            Usuario.full_name.ilike(f"%{q}%"),
            Usuario.username.ilike(f"%{q}%")
        ),
        Usuario.is_active == True
    ).limit(10).all()
    
    return [{"id": u.id, "text": u.full_name or u.username, "rol": u.rol} for u in results]

@router.get("/tiendas")
async def autocomplete_tiendas(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Búsqueda de tiendas/ubicaciones."""
    results = db.query(Tienda).filter(
        Tienda.nombre.ilike(f"%{q}%"),
        Tienda.is_active == True
    ).limit(10).all()
    
    return [{"id": t.id, "text": t.nombre, "direccion": t.direccion} for t in results]
