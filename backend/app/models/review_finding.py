
from sqlalchemy import (
    Column, Integer, String, Text, Float,
    ForeignKey, DateTime
)
from sqlalchemy.sql import func

from app.database.connection import Base


class ReviewFinding(Base):
    __tablename__ = "review_findings"

    id = Column(Integer, primary_key=True, index=True)

    submission_id = Column(
        Integer,
        ForeignKey("review_submissions.id"),
        nullable=False
    )

    finding_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="MEDIUM", nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    source_reference = Column(String(500), nullable=True)
    suggested_fix = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    verification_status = Column(
        String(50),
        nullable=True
    )

    status = Column(String(50), default="OPEN", nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
