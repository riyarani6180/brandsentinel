
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BrandAssetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)

    asset_type: str = Field(..., min_length=2, max_length=100)

    file_path: str = Field(..., min_length=1, max_length=500)

    description: Optional[str] = None

    is_approved: bool = False


class BrandAssetUpdate(BaseModel):
    name: Optional[str] = None

    asset_type: Optional[str] = None

    description: Optional[str] = None

    is_approved: Optional[bool] = None

    is_active: Optional[bool] = None


class BrandAssetResponse(BaseModel):
    id: int

    name: str

    asset_type: str

    file_path: str

    description: Optional[str] = None

    is_approved: bool

    is_active: bool

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
