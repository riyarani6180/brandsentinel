
from typing import Optional, Literal

from pydantic import BaseModel, Field


UserRole = Literal[
    "CREATOR",
    "BRAND_MANAGER",
    "AUTHORISED_REVIEWER",
    "BRAND_ADMIN"
]


class UserRoleUpdate(BaseModel):
    role: Optional[UserRole] = None

    is_active: Optional[bool] = None
