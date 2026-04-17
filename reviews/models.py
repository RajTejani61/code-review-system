from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code = Column(String, nullable=False)
    language = Column(String)

    security_review = Column(String, nullable=True)
    performance_review = Column(String, nullable=True)
    logic_review = Column(String, nullable=True)
    style_review = Column(String, nullable=True)
    
    final_report = Column(String, nullable=True)
    overall_score = Column(Integer, nullable=True)

    # Status tracking
    status = Column(String, default="pending") # pending | processing | completed | failed
    error_message = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationship back to user
    owner = relationship("User", back_populates="reviews")
