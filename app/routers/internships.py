"""Internship endpoints for index management and RAG-based matching."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Application, Resume, User
from app.resume_parser import normalize_candidate_data
from app.schemas import (
    CandidateInput,
    InternshipListResponse,
    InternshipMatchResponse,
)
from app.services.internship_matcher import _skills_match
from app.services.rag_service import get_rag_matches
from app.services.vector_store import (
    build_and_save_index,
    get_internship_by_id,
    load_internships,
)

router = APIRouter(prefix="/internships", tags=["Internships"])


@router.post("/build-index")
def build_index(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = db
    _ = current_user
    try:
        result = build_and_save_index(force_rebuild=True)
        return {
            "message": "Internship index built successfully.",
            **result,
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build internship index: {exc}",
        ) from exc


@router.get("", response_model=InternshipListResponse)
def list_internships() -> InternshipListResponse:
    internships = load_internships()
    return InternshipListResponse(total=len(internships), internships=internships)


@router.get("/match-all")
def match_all_internships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return ALL internships with per-internship skill match info for the user's active resume."""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    internships = load_internships()

    if not resumes:
        return {
            "has_active_resume": False,
            "reason": "NO_RESUME",
            "internships": internships,
            "applications": [],
        }

    active = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)  # noqa: E712
        .first()
    )

    if not active:
        return {
            "has_active_resume": False,
            "reason": "NO_ACTIVE_RESUME",
            "internships": internships,
            "applications": [],
        }

    try:
        parsed: dict[str, Any] = json.loads(active.parsed_data or "{}")
    except json.JSONDecodeError:
        parsed = {}

    normalized = normalize_candidate_data(parsed)

    user_apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    applied_ids = {a.internship_id for a in user_apps}

    results: list[dict[str, Any]] = []
    for internship in internships:
        matched_skills, missing_skills, pct = _skills_match(normalized, internship)
        results.append(
            {
                **internship,
                "is_match": len(missing_skills) == 0,
                "match_score": pct,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "already_applied": internship.get("id") in applied_ids,
            }
        )

    return {
        "has_active_resume": True,
        "active_resume_id": active.id,
        "active_resume_filename": active.filename,
        "resume_skills": normalized.get("skills", []),
        "internships": results,
        "applications": list(applied_ids),
    }


@router.get("/applications")
def get_user_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the authenticated user's internship applications."""
    apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    return [
        {
            "id": a.id,
            "internship_id": a.internship_id,
            "resume_id": a.resume_id,
            "applied_at": str(a.applied_at),
            "status": a.status,
        }
        for a in apps
    ]


@router.get("/{internship_id}")
def get_internship(internship_id: int):
    internship = get_internship_by_id(internship_id)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return internship


@router.post("/match", response_model=InternshipMatchResponse)
def match_from_candidate_data(
    candidate: CandidateInput,
    top_k: int = Query(default=5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    normalized = normalize_candidate_data(candidate.model_dump())
    try:
        matches = get_rag_matches(normalized, top_k=top_k)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail="Vector index not found. Build it first using /internships/build-index.",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Matching failed: {exc}") from exc

    return InternshipMatchResponse(
        candidate={
            "name": normalized.get("full_name", ""),
            "skills": normalized.get("skills", []),
        },
        matches=matches,
    )


@router.post("/match/{resume_id}", response_model=InternshipMatchResponse)
def match_from_resume_id(
    resume_id: int,
    top_k: int = Query(default=5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.user_id is not None and resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this resume")

    try:
        parsed_data: dict[str, Any] = json.loads(resume.parsed_data or "{}")
    except json.JSONDecodeError:
        parsed_data = {}

    normalized = normalize_candidate_data(parsed_data)
    if not normalized.get("full_name"):
        normalized["full_name"] = current_user.full_name
    if not normalized.get("email"):
        normalized["email"] = current_user.email

    try:
        matches = get_rag_matches(normalized, top_k=top_k)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail="Vector index not found. Build it first using /internships/build-index.",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Matching failed: {exc}") from exc

    return InternshipMatchResponse(
        candidate={
            "name": normalized.get("full_name", ""),
            "skills": normalized.get("skills", []),
        },
        matches=matches,
    )


@router.post("/{internship_id}/apply")
def apply_to_internship(
    internship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply to an internship using the user's active resume."""
    internship = get_internship_by_id(internship_id)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    active = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)  # noqa: E712
        .first()
    )
    if not active:
        raise HTTPException(status_code=400, detail="No active resume. Please activate a resume first.")

    existing = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.internship_id == internship_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You have already applied to this internship.")

    application = Application(
        user_id=current_user.id,
        internship_id=internship_id,
        resume_id=active.id,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Application submitted successfully",
        "application_id": application.id,
        "internship_id": internship_id,
        "resume_id": active.id,
    }
