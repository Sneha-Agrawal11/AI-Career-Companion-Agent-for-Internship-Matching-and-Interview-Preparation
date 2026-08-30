from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.database import engine
from app.models import Base

from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.resume import router as resume_router
from app.routers.internships import router as internship_router
from app.routers.chat import router as chat_router

app = FastAPI(
    title="AI Resume Parser API",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(internship_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {
        "message": "AI Resume Parser API is Running"
    }
