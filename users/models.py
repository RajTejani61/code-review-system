from database.database import Base
from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationship to reviews
    reviews = relationship("Review", back_populates="owner")
