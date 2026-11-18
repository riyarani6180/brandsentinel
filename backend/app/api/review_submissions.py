
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.review_submission import ReviewSubmission
from app.models.user import User
from app.schemas.review_submission import (
    ReviewSubmissionCreate,
    ReviewSubmissionUpdate,
    ReviewSubmissionResponse,
)
from app.services.review_service import analyze_submission
from app.services.audit_service import create_audit_log
from app.security.dependencies import get_current_user
from app.security.permissions import check_permission


router = APIRouter(
    prefix="/review-submissions",
    tags=["Review Submissions"]
)


def ensure_permission(current_user, permission):
    if not check_permission(current_user.role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )


def check_submission_access(submission, current_user):
    if (
        current_user.role == "CREATOR"
        and submission.submitted_by != current_user.email
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another user's submission."
        )


def get_submission_or_404(submission_id, db):
    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review submission not found."
        )

    return submission


def update_review_status(
    submission_id,
    new_status,
    permission,
    action,
    db,
    current_user
):
    ensure_permission(current_user, permission)

    submission = get_submission_or_404(submission_id, db)

    old_status = submission.status
    submission.status = new_status

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=action,
        entity_type="ReviewSubmission",
        entity_id=submission.id,
        details={
            "old_status": old_status,
            "new_status": new_status
        }
    )

    db.commit()
    db.refresh(submission)

    return {
        "message": f"Submission {new_status.lower()} successfully.",
        "submission": submission
    }


# CREATE SUBMISSION + AUTOMATIC COMPLIANCE ANALYSIS
@router.post(
    "/",
    response_model=ReviewSubmissionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_submission(
    submission_data: ReviewSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_permission(current_user, "CREATE_SUBMISSION")

    try:
        submission_values = submission_data.model_dump(
            exclude={"submitted_by"}
        )

        submission = ReviewSubmission(
            **submission_values,
            submitted_by=current_user.email
        )

        db.add(submission)
        db.flush()

        # Automatically analyze content after submission.
        analysis_result = analyze_submission(
            db=db,
            submission_id=submission.id
        )

        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="SUBMISSION_CREATED",
            entity_type="ReviewSubmission",
            entity_id=submission.id,
            details={
                "title": submission.title,
                "risk_score": analysis_result["risk_score"],
                "total_findings": analysis_result["total_findings"]
            }
        )

        db.commit()
        db.refresh(submission)

        return submission

    except Exception:
        db.rollback()
        raise


@router.get(
    "/",
    response_model=list[ReviewSubmissionResponse]
)
def get_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "CREATOR":
        ensure_permission(current_user, "VIEW_OWN_SUBMISSION")

        return (
            db.query(ReviewSubmission)
            .filter(
                ReviewSubmission.submitted_by == current_user.email
            )
            .order_by(ReviewSubmission.id.desc())
            .all()
        )

    ensure_permission(current_user, "VIEW_SUBMISSIONS")

    return (
        db.query(ReviewSubmission)
        .order_by(ReviewSubmission.id.desc())
        .all()
    )


@router.get(
    "/{submission_id}",
    response_model=ReviewSubmissionResponse
)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = get_submission_or_404(submission_id, db)

    if current_user.role == "CREATOR":
        ensure_permission(current_user, "VIEW_OWN_SUBMISSION")
        check_submission_access(submission, current_user)
    else:
        ensure_permission(current_user, "VIEW_SUBMISSIONS")

    return submission


@router.put(
    "/{submission_id}",
    response_model=ReviewSubmissionResponse
)
def update_submission(
    submission_id: int,
    submission_data: ReviewSubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_permission(current_user, "EDIT_OWN_SUBMISSION")

    submission = get_submission_or_404(submission_id, db)

    check_submission_access(submission, current_user)

    update_data = submission_data.model_dump(
        exclude_unset=True,
        exclude={"submitted_by", "status"}
    )

    for field, value in update_data.items():
        setattr(submission, field, value)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="SUBMISSION_UPDATED",
        entity_type="ReviewSubmission",
        entity_id=submission.id,
        details={"updated_fields": list(update_data.keys())}
    )

    db.commit()
    db.refresh(submission)

    return submission


@router.post("/{submission_id}/analyze")
def analyze_review_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_permission(current_user, "REVIEW_SUBMISSIONS")

    try:
        result = analyze_submission(
            db=db,
            submission_id=submission_id
        )

        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="SUBMISSION_ANALYZED",
            entity_type="ReviewSubmission",
            entity_id=submission_id,
            details={
                "risk_score": result["risk_score"],
                "status": result["status"],
                "total_findings": result["total_findings"]
            }
        )

        db.commit()

        return result

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.post("/{submission_id}/approve")
def approve_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_review_status(
        submission_id=submission_id,
        new_status="APPROVED",
        permission="APPROVE_SUBMISSIONS",
        action="SUBMISSION_APPROVED",
        db=db,
        current_user=current_user
    )


@router.post("/{submission_id}/reject")
def reject_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_review_status(
        submission_id=submission_id,
        new_status="REJECTED",
        permission="REJECT_SUBMISSIONS",
        action="SUBMISSION_REJECTED",
        db=db,
        current_user=current_user
    )


@router.post("/{submission_id}/request-changes")
def request_submission_changes(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_review_status(
        submission_id=submission_id,
        new_status="NEEDS_REVISION",
        permission="REQUEST_CHANGES",
        action="SUBMISSION_CHANGES_REQUESTED",
        db=db,
        current_user=current_user
    )


@router.delete("/{submission_id}")
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_permission(current_user, "EDIT_OWN_SUBMISSION")

    submission = get_submission_or_404(submission_id, db)

    check_submission_access(submission, current_user)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="SUBMISSION_DELETED",
        entity_type="ReviewSubmission",
        entity_id=submission.id,
        details={"title": submission.title}
    )

    db.delete(submission)
    db.commit()

    return {
        "message": "Review submission deleted successfully",
        "submission_id": submission_id
    }
