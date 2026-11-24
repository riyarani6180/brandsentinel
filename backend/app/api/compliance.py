
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.security.permissions import require_user_permission

from app.services.analytics_service import (
    get_compliance_overview,
    get_submission_trends,
    get_explainable_report,
    get_audit_activity_summary
)


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance Analytics"]
)


def validate_date_range(
    start_date: date | None,
    end_date: date | None
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date."
        )


@router.get("/overview")
def compliance_overview(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("VIEW_SUBMISSIONS")
    )
):
    validate_date_range(start_date, end_date)

    return get_compliance_overview(
        db,
        start_date,
        end_date
    )


@router.get("/trends")
def submission_trends(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("VIEW_SUBMISSIONS")
    )
):
    validate_date_range(start_date, end_date)

    return get_submission_trends(
        db,
        start_date,
        end_date
    )


@router.get("/reports/{submission_id}")
def explainable_submission_report(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("VIEW_SUBMISSIONS")
    )
):
    report = get_explainable_report(
        db,
        submission_id
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission report not found."
        )

    return report


@router.get("/audit-summary")
def audit_activity_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("VIEW_AUDIT_LOGS")
    )
):
    validate_date_range(start_date, end_date)

    return get_audit_activity_summary(
        db,
        start_date,
        end_date
    )
