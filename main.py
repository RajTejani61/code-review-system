from fastapi import FastAPI

from users.router import router as users_router
from reviews.router import router as reviews_router
from auth.router import auth_router

from database.database import Base, engine
import users.models
import reviews.models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Code Review System")

app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(auth_router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Code Review API is running"}

