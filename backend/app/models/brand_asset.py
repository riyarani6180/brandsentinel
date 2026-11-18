
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    asset_type = Column(String(100), nullable=False)

    file_path = Column(String(500), nullable=False)

    description = Column(Text, nullable=True)

    is_approved = Column(Boolean, default=False, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
