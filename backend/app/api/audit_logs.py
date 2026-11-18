
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.security.permissions import require_user_permission

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("/", response_model=list[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("VIEW_AUDIT_LOGS")
    )
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .all()
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("VIEW_AUDIT_LOGS")
    )
):
    audit_log = db.query(AuditLog).filter(
        AuditLog.id == log_id
    ).first()

    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found."
        )

    return audit_log
