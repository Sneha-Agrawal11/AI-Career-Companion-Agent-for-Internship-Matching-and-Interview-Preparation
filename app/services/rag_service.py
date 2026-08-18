"""Lightweight RAG service for internship recommendation reasoning."""

from __future__ import annotations

from typing import Any

from app.services.internship_matcher import match_internships


def _build_reason(candidate: dict[str, Any], match: dict[str, Any]) -> str:
    """Create deterministic, non-hallucinated explanation from retrieved context."""
    candidate_name = candidate.get("full_name") or "Candidate"
    matched_skills = match.get("matched_skills", [])
    missing_skills = match.get("missing_skills", [])

    reason_parts = [
        f"{candidate_name} matches this internship because "
        f"{', '.join(matched_skills[:4]) if matched_skills else 'some required skills'} "
        "appear in the resume and align with the internship requirements."
    ]

    if missing_skills:
        reason_parts.append(
            "Skills that can improve fit: " + ", ".join(missing_skills[:4]) + "."
        )

    reason_parts.append(
        f"Education compatibility is {match.get('education_match', 0)}% and "
        f"experience compatibility is {match.get('experience_match', 0)}%."
    )
    return " ".join(reason_parts)


def get_rag_matches(candidate: dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
    """Retrieve top internships and attach generated rationale."""
    base_matches = match_internships(candidate, top_k=top_k)
    enriched: list[dict[str, Any]] = []

    for match in base_matches:
        reason = _build_reason(candidate, match)
        enriched.append(
            {
                "internship_id": match["internship_id"],
                "title": match["title"],
                "company": match["company"],
                "domain": match["domain"],
                "location": match["location"],
                "work_mode": match["work_mode"],
                "duration": match["duration"],
                "stipend": match["stipend"],
                "semantic_similarity": match["semantic_similarity"],
                "skill_match_percentage": match["skill_match_percentage"],
                "education_match": match["education_match"],
                "experience_match": match["experience_match"],
                "final_score": match["final_score"],
                "matched_skills": match["matched_skills"],
                "missing_skills": match["missing_skills"],
                "reason": reason,
            }
        )

    return enriched
