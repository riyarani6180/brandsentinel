
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class GuidelineCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    source_filename: Optional[str] = None
    content: str = Field(..., min_length=1)


class GuidelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class GuidelineResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    source_filename: Optional[str] = None
    content: str
    version: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
