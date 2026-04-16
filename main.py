from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import engine, get_db, Base
from database import models
from database.models import User
from schemas.api_schemas import UserCreate, UserResponse

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Code Review System")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Code Review API is running"}


# User Endpoint
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create user
    db_user = User(
        email=user.email,
        password_hash=user.password # Temporary: storing plain
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

