
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ReviewCommentCreate(BaseModel):
    submission_id: int

    decision: str = Field(
        ...,
        pattern="^(APPROVED|REJECTED|CHANGES_REQUESTED)$"
    )

    comment: Optional[str] = None


class ReviewCommentResponse(BaseModel):
    id: int
    submission_id: int
    reviewer_name: str
    decision: str
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
