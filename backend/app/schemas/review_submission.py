
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ReviewSubmissionCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)

    content: str = Field(..., min_length=1)

    channel: Optional[str] = None

    submitted_by: Optional[str] = None


class ReviewSubmissionUpdate(BaseModel):
    title: Optional[str] = None

    content: Optional[str] = None

    channel: Optional[str] = None

    status: Optional[str] = None


class ReviewSubmissionResponse(BaseModel):
    id: int

    title: str

    content: str

    channel: Optional[str] = None

    submitted_by: Optional[str] = None

    status: str

    risk_score: int

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
