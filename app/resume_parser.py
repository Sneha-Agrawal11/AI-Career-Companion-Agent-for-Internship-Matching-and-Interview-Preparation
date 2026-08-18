"""Resume data normalization for internship matching workflows."""

from __future__ import annotations

from typing import Any

from app.utils import ensure_list, stringify_items

LIST_FIELDS = {
    "skills",
    "technical_skills",
    "soft_skills",
    "education",
    "work_experience",
    "internships",
    "projects",
    "certifications",
    "languages",
    "achievements",
}

SOFT_SKILL_HINTS = {
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "collaboration",
    "adaptability",
    "time management",
}


def _first_value(data: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, str) and first.strip():
                return first.strip()
    return default


def normalize_candidate_data(parsed_data: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize parsed resume data into a stable candidate structure."""
    source = parsed_data or {}

    skills = stringify_items(ensure_list(source.get("skills", [])))
    technical_skills = stringify_items(ensure_list(source.get("technical_skills", [])))
    soft_skills = stringify_items(ensure_list(source.get("soft_skills", [])))

    if not technical_skills and skills:
        technical_skills = [
            skill for skill in skills if skill.lower() not in SOFT_SKILL_HINTS
        ]
    if not soft_skills and skills:
        soft_skills = [skill for skill in skills if skill.lower() in SOFT_SKILL_HINTS]

    education = stringify_items(
        ensure_list(source.get("education", source.get("academic_background", [])))
    )

    work_experience = stringify_items(
        ensure_list(source.get("work_experience", source.get("experience", [])))
    )

    internships = stringify_items(ensure_list(source.get("internships", [])))
    if not internships:
        internships = [item for item in work_experience if "intern" in item.lower()]

    candidate = {
        "full_name": _first_value(source, ["full_name", "name"], ""),
        "email": _first_value(source, ["email", "emails"], ""),
        "phone": _first_value(source, ["phone", "phones"], ""),
        "address": _first_value(source, ["address"], ""),
        "linkedin": _first_value(source, ["linkedin"], ""),
        "github": _first_value(source, ["github"], ""),
        "professional_summary": _first_value(
            source,
            ["professional_summary", "summary", "objective"],
            "",
        ),
        "skills": skills,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "education": education,
        "work_experience": work_experience,
        "internships": internships,
        "projects": stringify_items(ensure_list(source.get("projects", []))),
        "certifications": stringify_items(ensure_list(source.get("certifications", []))),
        "languages": stringify_items(ensure_list(source.get("languages", []))),
        "achievements": stringify_items(ensure_list(source.get("achievements", []))),
        "other_relevant_information": stringify_items(
            ensure_list(source.get("other_relevant_information", []))
        ),
    }

    for field in LIST_FIELDS:
        candidate[field] = ensure_list(candidate.get(field, []))

    return candidate


def candidate_to_embedding_text(candidate: dict[str, Any]) -> str:
    """Create a normalized text representation used for embeddings."""
    sections = [
        ("Full Name", candidate.get("full_name", "")),
        ("Professional Summary", candidate.get("professional_summary", "")),
        ("Skills", ", ".join(candidate.get("skills", []))),
        ("Technical Skills", ", ".join(candidate.get("technical_skills", []))),
        ("Soft Skills", ", ".join(candidate.get("soft_skills", []))),
        ("Education", " ; ".join(candidate.get("education", []))),
        ("Work Experience", " ; ".join(candidate.get("work_experience", []))),
        ("Internships", " ; ".join(candidate.get("internships", []))),
        ("Projects", " ; ".join(candidate.get("projects", []))),
        ("Certifications", " ; ".join(candidate.get("certifications", []))),
        ("Languages", ", ".join(candidate.get("languages", []))),
        ("Achievements", " ; ".join(candidate.get("achievements", []))),
    ]

    lines = [f"{key}: {value}" for key, value in sections if value]
    return "\n".join(lines).strip()
