from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationship to reviews
    reviews = relationship("Review", back_populates="owner")

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

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationship back to user
    owner = relationship("User", back_populates="reviews")