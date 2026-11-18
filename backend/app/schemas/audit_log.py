
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None

    action: str = Field(..., min_length=2, max_length=150)

    entity_type: Optional[str] = None

    entity_id: Optional[int] = None

    details: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int

    user_id: Optional[int] = None

    action: str

    entity_type: Optional[str] = None

    entity_id: Optional[int] = None

    details: Optional[str] = None

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
