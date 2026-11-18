
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field


# Available roles in BrandSentinel
UserRole = Literal[
    "CREATOR",
    "BRAND_MANAGER",
    "AUTHORISED_REVIEWER",
    "BRAND_ADMIN"
]


# Schema for updating a user's role or account status
class UserRoleUpdate(BaseModel):

    role: Optional[UserRole] = None

    is_active: Optional[bool] = None

    model_config = ConfigDict(
        extra="forbid"
    )
