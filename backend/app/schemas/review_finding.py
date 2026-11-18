
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ReviewFindingCreate(BaseModel):
    submission_id: int

    finding_type: str = Field(..., min_length=2, max_length=100)

    severity: str = "MEDIUM"

    description: str = Field(..., min_length=1)

    evidence: Optional[str] = None

    source_reference: Optional[str] = None

    suggested_fix: Optional[str] = None

    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

    verification_status: Optional[str] = None


class ReviewFindingUpdate(BaseModel):
    severity: Optional[str] = None

    description: Optional[str] = None

    evidence: Optional[str] = None

    source_reference: Optional[str] = None

    suggested_fix: Optional[str] = None

    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

    verification_status: Optional[str] = None

    status: Optional[str] = None


class ReviewFindingResponse(BaseModel):
    id: int

    submission_id: int

    finding_type: str

    severity: str

    description: str

    evidence: Optional[str] = None

    source_reference: Optional[str] = None

    suggested_fix: Optional[str] = None

    confidence: Optional[float] = None

    verification_status: Optional[str] = None

    status: str

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
