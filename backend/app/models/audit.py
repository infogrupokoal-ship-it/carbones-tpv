import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, String, Text
from ..core.database import Base

class AuditLog(Base):
    """Corazón de la gobernanza Enterprise. Registro inmutable de acciones críticas."""
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), index=True)
    accion = Column(String(100), index=True) # EJ: DELETE_ORDER, CHANGE_PRICE, LOGIN
    tabla_afectada = Column(String(50))
    registro_id = Column(String(36))
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ReporteZ(Base):
    __tablename__ = "reportes_z"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha_cierre = Column(DateTime, default=datetime.utcnow)
    total_efectivo = Column(Float, default=0.0)
    total_tarjeta = Column(Float, default=0.0)
    total_ventas = Column(Float, default=0.0)
    arqueo_diferencia = Column(Float, default=0.0)
    resumen_ia = Column(Text, nullable=True) # Resumen narrativo generado por Gemini

class HardwareCommand(Base):
    __tablename__ = "hardware_commands"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comando = Column(String) # OPEN_DRAWER, PRINT_TICKET
    payload = Column(Text, nullable=True)
    estado = Column(String, default="PENDIENTE")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
