"""Internship endpoints for index management and RAG-based matching."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Resume, User
from app.resume_parser import normalize_candidate_data
from app.schemas import (
    CandidateInput,
    InternshipListResponse,
    InternshipMatchResponse,
)
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
