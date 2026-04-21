from fastapi import APIRouter, Depends, status, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.database import get_db
from auth.schemas import Token
from auth.utils import hash_password, verify_password
from users.models import User
from auth.oauth2 import create_access_token


auth_router = APIRouter(
    tags=["Authentication"]
)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    normalized_email = username.lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = hash_password(password)
    new_user = User(email=normalized_email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@auth_router.post("/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    normalized_email = user_credentials.username.lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")


    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")