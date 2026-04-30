from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....models.product import Producto, Categoria
from ....models.inventory import Ingrediente, RecetaItem
from ..deps import get_current_user, RoleChecker

router = APIRouter()

@router.get("/inventory/ingredients", response_model=List[Any])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(Ingrediente).all()

@router.post("/inventory/ingredients", status_code=21)
def create_ingredient(
    *,
    db: Session = Depends(get_db),
    name: str,
    unit: str,
    cost: float,
    current_user = Depends(RoleChecker(["ADMIN", "MANAGER"]))
):
    import uuid
    new_ing = Ingrediente(
        id=str(uuid.uuid4()),
        nombre=name,
        unidad_medida=unit,
        coste_por_unidad=cost
    )
    db.add(new_ing)
    db.commit()
    return new_ing

@router.post("/products/{product_id}/recipe")
def add_recipe_item(
    product_id: str,
    ingredient_id: str,
    quantity: float,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["ADMIN", "MANAGER"]))
):
    import uuid
    # Verificar existencia
    prod = db.query(Producto).filter(Producto.id == product_id).first()
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
        
    new_item = RecetaItem(
        id=str(uuid.uuid4()),
        producto_id=product_id,
        ingrediente_id=ingredient_id,
        cantidad_necesaria=quantity
    )
    db.add(new_item)
    db.commit()
    
    # Recalcular coste del producto
    from ....services.financials import FinancialService
    prod.coste_estimado = FinancialService.calculate_product_cost(db, product_id)
    db.commit()
    
    return {"status": "success", "new_cost": prod.coste_estimado}
