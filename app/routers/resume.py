import json

from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models import Resume

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

from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

UPLOAD_FOLDER = "app/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text_from_pdf(file_path)
    emails = extract_emails(resume_text)
    phones = extract_phone_numbers(resume_text)
    name = extract_name(resume_text)
    skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    experience = extract_experience(resume_text)
    analysis = analyze_resume(resume_text)


    parsed_result = {
    "name": name,
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

    resume = Resume(
    filename=file.filename,
    parsed_data=json.dumps(parsed_result)
) 

    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "filename": file.filename,
        "text": resume_text,
        "emails": emails,
        "phones": phones,
        "name": name,
        "skills": skills,
        "education": education,
        "experience": experience,
        "resume_score": analysis["resume_score"],
        "strengths": analysis["strengths"],
        "weaknesses": analysis["weaknesses"],
        "suggestions": analysis["suggestions"]

        
    }

@router.get("/all")
def get_all_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).all()

    return resumes