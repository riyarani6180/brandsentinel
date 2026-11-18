
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ApprovedFactCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)

    fact_content: str = Field(..., min_length=1)

    category: Optional[str] = None

    source_reference: Optional[str] = None

    valid_until: Optional[date] = None


class ApprovedFactUpdate(BaseModel):
    title: Optional[str] = None

    fact_content: Optional[str] = None

    category: Optional[str] = None

    source_reference: Optional[str] = None

    valid_until: Optional[date] = None

    is_active: Optional[bool] = None


class ApprovedFactResponse(BaseModel):
    id: int

    title: str

    fact_content: str

    category: Optional[str] = None

    source_reference: Optional[str] = None

    valid_until: Optional[date] = None

    is_active: bool

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
