"""Preparation Agent router — dedicated endpoints for the Preparation Agent.

Reuses existing:
  - Authentication (get_current_user)
  - Database (get_db, ChatSession, ChatMessage, Resume)
  - LLM (chat_service singleton — Groq client)
  - Internship data (get_internship_by_id, load_internships)
  - Resume upload (same /resume/upload endpoint)

Sessions created here use agent_type='preparation' to stay isolated
from the Product Assistant (agent_type='product').
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json, os, shutil

from app.database import get_db
from app.models import User, ChatSession, ChatMessage, Resume
from app.schemas import ChatSessionResponse, ChatMessageResponse
from app.dependencies import get_current_user
from app.services.chat_service import chat_service
from app.services.vector_store import get_internship_by_id, load_internships

from pydantic import BaseModel

# ---- Schemas (local, minimal) ----

class PrepSessionCreate(BaseModel):
    title: str | None = "New Preparation"

class PrepMessageCreate(BaseModel):
    message: str
    internship_id: int | None = None

class PrepSessionResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
    title: str
    agent_type: str
    created_at: datetime
    updated_at: datetime


router = APIRouter(
    prefix="/prep",
    tags=["Preparation Agent"],
)

AGENT_TYPE = "preparation"

# ---- Sessions ----

@router.get("/sessions", response_model=List[PrepSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id, ChatSession.agent_type == AGENT_TYPE)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

@router.post("/sessions", response_model=PrepSessionResponse)
def create_session(
    body: PrepSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ChatSession(
        user_id=current_user.id,
        title=body.title,
        agent_type=AGENT_TYPE,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.agent_type == AGENT_TYPE,
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")
    db.delete(session)
    db.commit()
    return {"ok": True}

# ---- Messages ----

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.agent_type == AGENT_TYPE,
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def send_message(
    session_id: int,
    body: PrepMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.agent_type == AGENT_TYPE,
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")

    # Store user message
    user_msg = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        role="user",
        message=body.message,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Fetch history (last 20 messages)
    history_records = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.id <= user_msg.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()
    )
    history_records.reverse()
    chat_history = [{"role": m.role, "message": m.message} for m in history_records[:-1]]

    # Fetch user's active resume
    resume_data = None
    active_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)  # noqa: E712
        .first()
    )
    if active_resume:
        try:
            resume_data = json.loads(active_resume.parsed_data or "{}")
        except json.JSONDecodeError:
            resume_data = None

    # Fetch internship if provided
    internship_data = None
    if body.internship_id:
        internship_data = get_internship_by_id(body.internship_id)

    # Build preparation-specific system prompt + call LLM
    ai_text = _generate_prep_response(
        user_message=body.message,
        chat_history=chat_history,
        resume_data=resume_data,
        internship_data=internship_data,
    )

    ai_msg = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        role="assistant",
        message=ai_text,
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    # Update session metadata
    session.updated_at = datetime.utcnow()
    if len(history_records) == 1 and session.title == "New Preparation":
        session.title = body.message[:40] + ("…" if len(body.message) > 40 else "")
    db.commit()

    return ai_msg

# ---- File upload (reuses existing resume parsing) ----

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a resume/document inside the Preparation Agent.
    Reuses the existing resume parsing pipeline and saves to the Resume table.
    """
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF and DOCX files are allowed.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # Reuse existing parsing utilities
    from utils import (
        extract_text_from_pdf,
        extract_emails,
        extract_phone_numbers,
        extract_name,
        extract_skills,
        extract_education,
        extract_experience,
        analyze_resume,
    )

    resume_text = extract_text_from_pdf(file_path)
    emails = extract_emails(resume_text)
    phones = extract_phone_numbers(resume_text)
    name_val = extract_name(resume_text)
    skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    experience = extract_experience(resume_text)
    analysis = analyze_resume(resume_text)

    parsed_result = {
        "name": name_val,
        "emails": emails,
        "phones": phones,
        "skills": skills,
        "education": education,
        "experience": experience,
        "resume_score": analysis["resume_score"],
        "strengths": analysis["strengths"],
        "weaknesses": analysis["weaknesses"],
        "suggestions": analysis["suggestions"],
    }

    # Deactivate old resumes, save new one as active
    db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
    resume = Resume(
        filename=file.filename,
        parsed_data=json.dumps(parsed_result),
        user_id=current_user.id,
        is_active=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Document uploaded and parsed",
        "resume_id": resume.id,
        "filename": file.filename,
        "parsed": parsed_result,
    }

# ---- Internship list (for selection UI) ----

@router.get("/internships")
def list_internships_for_selection():
    """Return a lightweight list of all internships for the selector dropdown."""
    internships = load_internships()
    return [
        {
            "id": i.get("id"),
            "title": i.get("title"),
            "company": i.get("company"),
            "domain": i.get("domain"),
        }
        for i in internships
    ]


# ---- LLM response generation (preparation-specific) ----

def _format_resume(resume_data: dict) -> str:
    sections = []
    if resume_data.get("name"):
        sections.append(f"Name: {resume_data['name']}")
    skills = resume_data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",")]
    if skills:
        sections.append(f"Skills: {', '.join(skills)}")
    edu = resume_data.get("education", [])
    if edu:
        sections.append(f"Education: {'; '.join(str(e) for e in edu)}")
    exp = resume_data.get("experience", [])
    if exp:
        sections.append(f"Experience: {'; '.join(str(e) for e in exp)}")
    projects = resume_data.get("projects", [])
    if isinstance(projects, list) and projects:
        sections.append(f"Projects: {'; '.join(str(p) for p in projects)}")
    certs = resume_data.get("certifications", [])
    if isinstance(certs, list) and certs:
        sections.append(f"Certifications: {', '.join(str(c) for c in certs)}")
    summary = resume_data.get("professional_summary") or resume_data.get("summary", "")
    if summary:
        sections.append(f"Summary: {summary}")
    score = resume_data.get("resume_score")
    if score is not None:
        sections.append(f"Resume Score: {score}")
    strengths = resume_data.get("strengths", [])
    if isinstance(strengths, list) and strengths:
        sections.append(f"Strengths: {'; '.join(str(s) for s in strengths)}")
    weaknesses = resume_data.get("weaknesses", [])
    if isinstance(weaknesses, list) and weaknesses:
        sections.append(f"Weaknesses: {'; '.join(str(w) for w in weaknesses)}")
    return "\n".join(sections) if sections else ""


def _format_internship(internship: dict) -> str:
    sections = []
    for key in ("title", "company", "domain", "description"):
        if internship.get(key):
            sections.append(f"{key.title()}: {internship[key]}")
    req = internship.get("required_skills", [])
    if req:
        sections.append(f"Required Skills: {', '.join(req)}")
    pref = internship.get("preferred_skills", [])
    if pref:
        sections.append(f"Preferred Skills: {', '.join(pref)}")
    for key in ("education_requirements", "experience_requirements"):
        if internship.get(key):
            sections.append(f"{key.replace('_', ' ').title()}: {internship[key]}")
    resp = internship.get("responsibilities", [])
    if resp:
        sections.append(f"Responsibilities: {'; '.join(resp)}")
    for key in ("location", "work_mode", "duration", "stipend", "eligibility"):
        if internship.get(key):
            sections.append(f"{key.replace('_', ' ').title()}: {internship[key]}")
    return "\n".join(sections) if sections else ""


def _skill_match(resume_data: dict, internship: dict) -> str:
    skills_raw = resume_data.get("skills", [])
    if isinstance(skills_raw, str):
        skills_raw = [s.strip() for s in skills_raw.split(",")]
    user_skills = {s.lower() for s in skills_raw if s}
    required = internship.get("required_skills", [])
    matched = [s for s in required if s.lower() in user_skills]
    missing = [s for s in required if s.lower() not in user_skills]
    pct = round(len(matched) / len(required) * 100, 1) if required else 100.0
    return (
        f"Skill Match: {pct}%\n"
        f"Matched: {', '.join(matched) if matched else 'None'}\n"
        f"Missing: {', '.join(missing) if missing else 'None — all matched!'}"
    )


def _generate_prep_response(
    user_message: str,
    chat_history: list,
    resume_data: dict | None,
    internship_data: dict | None,
) -> str:
    """Build system prompt for the Preparation Agent and call the shared LLM."""

    parts = [
        "You are the InternMatch Preparation Agent — an advanced AI career coach and mock interviewer.\n"
        "You help users prepare for internships and job interviews with personalized guidance.\n\n"
    ]

    # Resume context
    if resume_data:
        parts.append(f"USER'S ACTIVE RESUME:\n{_format_resume(resume_data)}\n\n")
    else:
        parts.append(
            "NOTE: The user has not uploaded/activated a resume yet. "
            "Suggest they upload one using the attachment button for personalized guidance. "
            "You can still provide general preparation help.\n\n"
        )

    # Internship context
    if internship_data:
        parts.append(f"TARGET INTERNSHIP / JOB:\n{_format_internship(internship_data)}\n\n")
        if resume_data:
            parts.append(f"SKILL MATCHING:\n{_skill_match(resume_data, internship_data)}\n\n")
    else:
        parts.append(
            "NOTE: No specific internship is selected. "
            "If the user asks to prepare for a specific role, ask them to select an internship or describe the role. "
            "You can still help with general interview preparation, resume analysis, and career guidance.\n\n"
        )

    parts.append(
        "CAPABILITIES — you can help with ALL of these:\n"
        "• Resume analysis and improvement suggestions\n"
        "• Internship/job preparation plans\n"
        "• Skill gap identification and study roadmaps\n"
        "• Technical interview questions (coding, system design, domain-specific)\n"
        "• Behavioral / HR interview questions (STAR method)\n"
        "• Mock interviews (one question at a time, with evaluation)\n"
        "• Answer evaluation with scores, strengths, weaknesses, and improvements\n"
        "• Questions about uploaded documents\n"
        "• General career and professional development guidance\n\n"

        "BEHAVIOR RULES:\n"
        "1. When conducting a mock interview: ask ONE question at a time. Wait for the user's answer. "
        "Then evaluate their answer (score out of 10, strengths, weaknesses, improved answer). "
        "Then ask the next question, adapting difficulty based on performance.\n"
        "2. When the user asks to prepare for a specific internship and internship context is provided above, "
        "USE IT DIRECTLY. Do NOT ask the user to provide the job description again.\n"
        "3. When starting a preparation session, briefly outline the preparation plan, then begin interactively.\n"
        "4. Start with easier questions and progressively increase difficulty.\n"
        "5. Focus more on missing/weak skills to help the user improve.\n"
        "6. Be conversational, supportive, and professional — like a real senior mentor.\n"
        "7. Do NOT fabricate information about the user. Use only what's in the resume.\n"
        "8. If asked about the uploaded resume/document, reference the actual parsed data above.\n"
        "9. For skill gaps, create actionable study plans with specific resources when possible.\n"
        "10. Use markdown formatting (bold, bullets, numbered lists) for readability.\n"
    )

    system_prompt = "".join(parts)

    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["message"]})
    messages.append({"role": "user", "content": user_message})

    try:
        response = chat_service.llm_client.chat.completions.create(
            model=chat_service.model,
            messages=messages,
            temperature=0.35,
            max_tokens=1800,
        )
        return response.choices[0].message.content
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"I'm sorry, I encountered an error: {str(e)}"
