from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional
from ..database import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    """Repositorio genérico para operaciones CRUD estándar."""
    
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[T]:
        return self.db.query(self.model).get(id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, id: str) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            return True
        return False
