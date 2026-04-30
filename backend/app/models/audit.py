import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from ..core.database import Base

class AuditLog(Base):
    """Registro inmutable de acciones críticas."""
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(36), nullable=True)
    action = Column(String(50)) # CREATE, UPDATE, DELETE, LOGIN
    entity = Column(String(50)) # Pedido, Producto, etc.
    details = Column(JSON)
    ip_address = Column(String(45))
