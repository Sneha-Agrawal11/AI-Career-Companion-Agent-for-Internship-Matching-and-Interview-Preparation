"""Business logic for internship matching and scoring."""

from __future__ import annotations

import re
from typing import Any

from app.resume_parser import candidate_to_embedding_text
from app.services.embedding_service import get_embedding_service
from app.services.vector_store import search_internships
from app.utils import unique_lower

SEMANTIC_WEIGHT = 0.50
SKILL_WEIGHT = 0.30
COMPATIBILITY_WEIGHT = 0.20


def _extract_years(experience_texts: list[str]) -> float:
    years = 0.0
    year_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)", re.IGNORECASE)
    for text in experience_texts:
        match = year_pattern.search(text)
        if match:
            years = max(years, float(match.group(1)))
    return years


def _education_match(candidate_education: list[str], requirement: str) -> float:
    if not requirement:
        return 100.0

    candidate_text = " ".join(candidate_education).lower()
    requirement_lower = requirement.lower()

    if any(keyword in candidate_text for keyword in ["b.tech", "bachelor", "b.e", "bsc"]):
        if any(keyword in requirement_lower for keyword in ["b.tech", "bachelor", "b.e", "bsc"]):
            return 100.0
    if any(keyword in candidate_text for keyword in ["m.tech", "master", "msc", "mca"]):
        return 100.0
    return 45.0


def _experience_match(candidate_experience: list[str], requirement: str) -> float:
    if not requirement:
        return 100.0

    candidate_years = _extract_years(candidate_experience)

    required_year_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)", re.IGNORECASE)
    required_match = required_year_pattern.search(requirement or "")
    if not required_match:
        if "fresher" in requirement.lower() or "entry" in requirement.lower():
            return 100.0
        return 65.0

    required_years = float(required_match.group(1))
    if candidate_years >= required_years:
        return 100.0
    if candidate_years == 0 and required_years <= 1:
        return 80.0

    ratio = max(0.0, min(candidate_years / required_years, 1.0))
    return round(ratio * 100.0, 2)


def _skills_match(candidate: dict[str, Any], internship: dict[str, Any]) -> tuple[list[str], list[str], float]:
    candidate_skills_raw = (
        candidate.get("skills", [])
        + candidate.get("technical_skills", [])
        + candidate.get("soft_skills", [])
    )
    candidate_skills = unique_lower(candidate_skills_raw)

    required_skills = internship.get("required_skills", [])
    required_lookup = {skill.lower(): skill for skill in required_skills}

    matched = [original for lower, original in required_lookup.items() if lower in candidate_skills]
    missing = [original for lower, original in required_lookup.items() if lower not in candidate_skills]

    if not required_skills:
        return matched, missing, 100.0

    percentage = (len(matched) / len(required_skills)) * 100.0
    return matched, missing, round(percentage, 2)


def _compute_final_score(semantic_similarity: float, skill_match: float, compatibility: float) -> float:
    """Scoring formula: semantic(50%) + skill(30%) + compatibility(20%)."""
    semantic_score = max(0.0, min(semantic_similarity, 1.0)) * 100.0
    final_score = (
        semantic_score * SEMANTIC_WEIGHT
        + skill_match * SKILL_WEIGHT
        + compatibility * COMPATIBILITY_WEIGHT
    )
    return round(final_score, 2)


def match_internships(candidate: dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
    """Match candidate profile with internship records using semantic search and rule scoring."""
    candidate_text = candidate_to_embedding_text(candidate)
    embedding = get_embedding_service().encode_text(candidate_text)

    search_results = search_internships(embedding, top_k=top_k)
    matches: list[dict[str, Any]] = []

    for item in search_results:
        internship = item["internship"]
        semantic_similarity = float(item["semantic_similarity"])

        matched_skills, missing_skills, skill_percentage = _skills_match(candidate, internship)

        education_score = _education_match(
            candidate.get("education", []),
            internship.get("education_requirements", ""),
        )
        experience_score = _experience_match(
            candidate.get("work_experience", []),
            internship.get("experience_requirements", ""),
        )
        compatibility = round((education_score + experience_score) / 2.0, 2)

        final_score = _compute_final_score(
            semantic_similarity=semantic_similarity,
            skill_match=skill_percentage,
            compatibility=compatibility,
        )

        matches.append(
            {
                "internship_id": internship.get("id"),
                "title": internship.get("title", ""),
                "company": internship.get("company", ""),
                "domain": internship.get("domain", ""),
                "location": internship.get("location", ""),
                "work_mode": internship.get("work_mode", ""),
                "duration": internship.get("duration", ""),
                "stipend": internship.get("stipend", ""),
                "semantic_similarity": round(semantic_similarity, 4),
                "skill_match_percentage": skill_percentage,
                "education_match": round(education_score, 2),
                "experience_match": round(experience_score, 2),
                "final_score": final_score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "internship": internship,
            }
        )

    return sorted(matches, key=lambda item: item["final_score"], reverse=True)
