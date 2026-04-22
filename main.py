from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from users.router import router as users_router
from reviews.router import router as reviews_router
from auth.router import auth_router

from database.database import Base, engine
import users.models
import reviews.models
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip DB setup when running under pytest (tests create their own SQLite tables).
    if not os.getenv("TESTING"):
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Code Review System", lifespan=lifespan)

app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(auth_router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Code Review API is running"}

