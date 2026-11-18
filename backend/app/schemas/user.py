
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict, EmailStr


UserRole = Literal[
    "CREATOR",
    "BRAND_MANAGER",
    "AUTHORISED_REVIEWER",
    "BRAND_ADMIN"
]


class UserCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8
    )

    role: UserRole = "CREATOR"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
