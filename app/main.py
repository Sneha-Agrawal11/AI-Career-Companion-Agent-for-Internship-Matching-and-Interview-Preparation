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
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Migrate: add is_active column to resumes table if not present
from sqlalchemy import inspect as sa_inspect, text as sa_text
_inspector = sa_inspect(engine)
_resume_cols = [c["name"] for c in _inspector.get_columns("resumes")]
if "is_active" not in _resume_cols:
    with engine.connect() as _conn:
        _conn.execute(sa_text("ALTER TABLE resumes ADD COLUMN is_active BOOLEAN DEFAULT 0"))
        _conn.commit()

# Migrate: add agent_type column to chat_sessions table if not present
_chat_cols = [c["name"] for c in _inspector.get_columns("chat_sessions")]
if "agent_type" not in _chat_cols:
    with engine.connect() as _conn:
        _conn.execute(sa_text("ALTER TABLE chat_sessions ADD COLUMN agent_type VARCHAR DEFAULT 'product'"))
        _conn.commit()

from app.routers.prep_agent import router as prep_agent_router

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(internship_router)
app.include_router(chat_router)
app.include_router(prep_agent_router)

@app.get("/")
def read_root():
    return {
        "message": "AI Resume Parser API is Running"
    }
