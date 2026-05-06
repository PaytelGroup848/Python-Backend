from app.db.database import SessionLocal
from app.models.audit import AuditLog

def log_action(user_id: int, action: str, endpoint: str):
    db = SessionLocal()

    log = AuditLog(
        user_id=user_id,
        action=action,
        endpoint=endpoint
    )

    db.add(log)
    db.commit()
    db.close()