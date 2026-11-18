
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class ReviewSubmission(Base):
    __tablename__ = "review_submissions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=False)

    channel = Column(String(100), nullable=True)

    submitted_by = Column(String(150), nullable=True)

    status = Column(
        String(50),
        default="PENDING",
        nullable=False
    )

    risk_score = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
