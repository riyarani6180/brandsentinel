
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.review_submission import ReviewSubmission
from app.models.review_comment import ReviewComment
from app.models.user import User

from app.schemas.review_comment import (
    ReviewCommentCreate,
    ReviewCommentResponse,
)

from app.security.dependencies import get_current_user
from app.security.permissions import check_permission


router = APIRouter(
    prefix="/review-comments",
    tags=["Review Comments"]
)


# Submit an authenticated reviewer's decision
@router.post(
    "/",
    response_model=ReviewCommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_review_comment(
    review_data: ReviewCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether the submission exists.
    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == review_data.submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review submission not found"
        )

    # Determine the permission required for this decision.
    permission_map = {
        "APPROVED": "APPROVE_SUBMISSIONS",
        "REJECTED": "REJECT_SUBMISSIONS",
        "CHANGES_REQUESTED": "REQUEST_CHANGES"
    }

    required_permission = permission_map[review_data.decision]

    if not check_permission(
        current_user.role,
        required_permission
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to make this review decision."
        )

    # High-risk submissions require an authorised reviewer.
    if submission.risk_score >= 60:
        if current_user.role != "AUTHORISED_REVIEWER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="High-risk submissions require an authorised reviewer."
            )

    # Update submission status.
    submission.status = review_data.decision

    # Save the authenticated reviewer's identity.
    review_comment = ReviewComment(
        submission_id=review_data.submission_id,
        reviewer_name=current_user.full_name,
        decision=review_data.decision,
        comment=review_data.comment
    )

    db.add(review_comment)
    db.commit()
    db.refresh(review_comment)

    return review_comment


# Retrieve review history
@router.get(
    "/submission/{submission_id}",
    response_model=list[ReviewCommentResponse]
)
def get_review_comments(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only users with submission viewing permission can access history.
    if not check_permission(
        current_user.role,
        "VIEW_SUBMISSIONS"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view review history."
        )

    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review submission not found"
        )

    return (
        db.query(ReviewComment)
        .filter(ReviewComment.submission_id == submission_id)
        .order_by(ReviewComment.id.desc())
        .all()
    )
