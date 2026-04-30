import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)
    pin_hash = Column(String(128), nullable=True) # Hashed PIN para TPV
    email = Column(String, nullable=True)
    rol = Column(String, default="CASHIER") # ADMIN, MANAGER, CASHIER, KITCHEN
    is_active = Column(Boolean, default=True)
    
    fichajes = relationship("Fichaje", back_populates="usuario")
    created_at = Column(DateTime, default=datetime.utcnow)

class Fichaje(Base):
    __tablename__ = "fichajes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    tipo = Column(String) # ENTRADA, SALIDA, INICIO_PAUSA, FIN_PAUSA
    fecha = Column(DateTime, default=datetime.utcnow)
    latitud = Column(String, nullable=True)
    longitud = Column(String, nullable=True)
    
    usuario = relationship("Usuario", back_populates="fichajes")
