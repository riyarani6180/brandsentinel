
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class Guideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    source_filename = Column(String(255), nullable=True)

    content = Column(Text, nullable=False)

    version = Column(Integer, default=1, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
