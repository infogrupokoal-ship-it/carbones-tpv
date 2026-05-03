import logging
import datetime
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models import AuditLog

logger = logging.getLogger("QuantumAudit")

class AdminAuditService:
    """
    Industrial-grade audit service for administrative actions.
    Tracks CRUD operations and configuration changes.
    """
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                action=action.upper(),
                resource=resource.upper(),
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            db.add(audit_entry)
            db.commit()
            
            logger.info(f"[AUDIT] {user_id} | {action} | {resource} | {resource_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"[AUDIT_FAIL] {str(e)}")

    @staticmethod
    def get_recent_logs(db: Session, limit: int = 50):
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()

admin_audit = AdminAuditService()
