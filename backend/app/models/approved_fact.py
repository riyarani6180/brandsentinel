
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class ApprovedFact(Base):
    __tablename__ = "approved_facts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    fact_content = Column(Text, nullable=False)

    category = Column(String(100), nullable=True)

    source_reference = Column(String(500), nullable=True)

    valid_until = Column(Date, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
