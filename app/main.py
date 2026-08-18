from fastapi import FastAPI

from app.database import engine
from app.models import Base

from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.resume import router as resume_router
from app.routers.internships import router as internship_router

app = FastAPI(
    title="AI Resume Parser API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(internship_router)

@app.get("/")
def read_root():
    return {
        "message": "AI Resume Parser API is Running"
    }
