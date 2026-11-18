
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.review_finding import ReviewFinding
from app.models.review_submission import ReviewSubmission
from app.models.user import User
from app.schemas.review_finding import (
    ReviewFindingCreate,
    ReviewFindingUpdate,
    ReviewFindingResponse,
)
from app.security.dependencies import get_current_user
from app.security.permissions import require_permission


router = APIRouter(
    prefix="/review-findings",
    tags=["Review Findings"]
)


def check_finding_access(submission, current_user):
    """Check whether the logged-in user can access a submission."""

    if current_user.role == "CREATOR":
        if submission.submitted_by != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access findings for another creator's submission."
            )
    else:
        require_permission(
            current_user.role,
            "VIEW_SUBMISSIONS"
        )


# CREATE FINDING - BRAND_MANAGER / AUTHORISED_REVIEWER
@router.post(
    "/",
    response_model=ReviewFindingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_finding(
    finding_data: ReviewFindingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(
        current_user.role,
        "REVIEW_SUBMISSIONS"
    )

    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == finding_data.submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review submission not found"
        )

    finding = ReviewFinding(**finding_data.model_dump())

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


# VIEW ALL FINDINGS
@router.get(
    "/",
    response_model=list[ReviewFindingResponse]
)
def get_findings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ReviewFinding)

    if current_user.role == "CREATOR":
        query = (
            query.join(
                ReviewSubmission,
                ReviewFinding.submission_id == ReviewSubmission.id
            )
            .filter(
                ReviewSubmission.submitted_by == current_user.email
            )
        )
    else:
        require_permission(
            current_user.role,
            "VIEW_SUBMISSIONS"
        )

    return (
        query.order_by(ReviewFinding.id.desc())
        .all()
    )


# VIEW FINDINGS FOR ONE SUBMISSION
@router.get(
    "/submission/{submission_id}",
    response_model=list[ReviewFindingResponse]
)
def get_submission_findings(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review submission not found"
        )

    check_finding_access(submission, current_user)

    return (
        db.query(ReviewFinding)
        .filter(ReviewFinding.submission_id == submission_id)
        .order_by(ReviewFinding.id.desc())
        .all()
    )


# VIEW ONE FINDING
@router.get(
    "/{finding_id}",
    response_model=ReviewFindingResponse
)
def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(ReviewFinding).filter(
        ReviewFinding.id == finding_id
    ).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review finding not found"
        )

    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == finding.submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Related submission not found"
        )

    check_finding_access(submission, current_user)

    return finding


# UPDATE FINDING - BRAND_MANAGER / AUTHORISED_REVIEWER
@router.put(
    "/{finding_id}",
    response_model=ReviewFindingResponse
)
def update_finding(
    finding_id: int,
    finding_data: ReviewFindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(
        current_user.role,
        "REVIEW_SUBMISSIONS"
    )

    finding = db.query(ReviewFinding).filter(
        ReviewFinding.id == finding_id
    ).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review finding not found"
        )

    update_data = finding_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update information provided."
        )

    for field, value in update_data.items():
        setattr(finding, field, value)

    db.commit()
    db.refresh(finding)

    return finding


# DELETE FINDING - BRAND_ADMIN ONLY
@router.delete("/{finding_id}")
def delete_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(
        current_user.role,
        "MANAGE_GUIDELINES"
    )

    finding = db.query(ReviewFinding).filter(
        ReviewFinding.id == finding_id
    ).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review finding not found"
        )

    db.delete(finding)
    db.commit()

    return {
        "message": "Review finding deleted successfully",
        "finding_id": finding_id
    }
