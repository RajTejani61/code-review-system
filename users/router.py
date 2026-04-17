from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from typing import List

from users.models import User
from users.schemas import UserCreate, UserResponse
from reviews.models import Review
from reviews.schemas import ReviewSummary
import utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# User Endpoint
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # Hash the password
    hashed_password = utils.hash(user.password)

    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create user
    db_user = User(
        email=user.email,
        password_hash=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Get User Review History Endpoint
@router.get("/{user_id}/reviews", response_model=List[ReviewSummary])
def get_user_review_history(user_id: int, db: Session = Depends(get_db)):
    
    reviews = db.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()
    return reviews
