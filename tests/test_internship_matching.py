"""Tests for RAG-based internship matching service."""

from __future__ import annotations

import pytest

from app.services.rag_service import get_rag_matches
from app.services.vector_store import build_and_save_index


CANDIDATE_PROFILES = [
    {
        "label": "AI/ML candidate",
        "candidate": {
            "full_name": "Aarav Mehta",
            "skills": ["Python", "Machine Learning", "NumPy", "Pandas", "Scikit-learn"],
            "education": ["B.Tech Computer Science"],
            "work_experience": ["ML Intern - 1 year"],
            "projects": ["Image classification using CNN"],
        },
        "expected_domain": {"AI/ML", "Machine Learning"},
    },
    {
        "label": "Backend developer",
        "candidate": {
            "full_name": "Neha Sharma",
            "skills": ["Python", "FastAPI", "SQL", "Git", "Docker"],
            "education": ["B.E. Information Technology"],
            "work_experience": ["Backend Intern - 8 months"],
            "projects": ["Order management REST API"],
        },
        "expected_domain": {"Backend Development", "Python Development", "Software Engineering"},
    },
    {
        "label": "Data Science candidate",
        "candidate": {
            "full_name": "Kritika Rao",
            "skills": ["Python", "SQL", "Pandas", "Data Visualization", "Statistics"],
            "education": ["B.Sc Data Science"],
            "work_experience": ["Data Analyst Intern - 1 year"],
            "projects": ["Churn prediction dashboard"],
        },
        "expected_domain": {"Data Science", "Data Engineering"},
    },
    {
        "label": "Generative AI candidate",
        "candidate": {
            "full_name": "Rahul Singh",
            "skills": ["Python", "Prompt Engineering", "LLM Fundamentals", "RAG", "APIs"],
            "education": ["B.Tech AI and Data Science"],
            "work_experience": ["GenAI Intern - 6 months"],
            "projects": ["RAG chatbot with vector search"],
        },
        "expected_domain": {"Generative AI", "AI/ML"},
    },
    {
        "label": "Frontend full stack candidate",
        "candidate": {
            "full_name": "Isha Kapoor",
            "skills": ["JavaScript", "React", "HTML", "CSS", "Node.js", "TypeScript"],
            "education": ["BCA"],
            "work_experience": ["Frontend Intern - 1 year"],
            "projects": ["E-commerce frontend with React"],
        },
        "expected_domain": {"Frontend Development", "Full Stack Development"},
    },
    {
        "label": "Java candidate",
        "candidate": {
            "full_name": "Aditya Verma",
            "skills": ["Java", "Spring Boot", "SQL", "Git", "JUnit"],
            "education": ["B.Tech Information Technology"],
            "work_experience": ["Java trainee - 1 year"],
            "projects": ["Student portal backend"],
        },
        "expected_domain": {"Java Development", "Software Engineering"},
    },
    {
        "label": "Cloud DevOps candidate",
        "candidate": {
            "full_name": "Sana Fatima",
            "skills": ["Linux", "Docker", "CI/CD", "AWS", "Kubernetes"],
            "education": ["B.Tech Computer Engineering"],
            "work_experience": ["DevOps Intern - 1 year"],
            "projects": ["CI pipeline with container deployment"],
        },
        "expected_domain": {"Cloud/DevOps", "Software Engineering"},
    },
    {
        "label": "Data engineering candidate",
        "candidate": {
            "full_name": "Vikram Nair",
            "skills": ["Python", "SQL", "ETL", "Data Modeling", "Airflow"],
            "education": ["B.Tech Computer Science"],
            "work_experience": ["Data Engineering Intern - 1 year"],
            "projects": ["Batch data pipeline on cloud"],
        },
        "expected_domain": {"Data Engineering", "Data Science"},
    },
]


@pytest.fixture(scope="session", autouse=True)
def ensure_index() -> None:
    build_and_save_index(force_rebuild=True)


@pytest.mark.parametrize("profile", CANDIDATE_PROFILES)
def test_candidate_matching(profile: dict) -> None:
    candidate = profile["candidate"]
    matches = get_rag_matches(candidate, top_k=5)

    assert len(matches) == 5
    assert all(0.0 <= item["semantic_similarity"] <= 1.0 for item in matches)
    assert all(0.0 <= item["skill_match_percentage"] <= 100.0 for item in matches)
    assert all(0.0 <= item["final_score"] <= 100.0 for item in matches)

    domains = {item["domain"] for item in matches}
    assert domains.intersection(profile["expected_domain"])

    print(f"\nCandidate: {profile['label']}")
    for item in matches:
        print(
            " | ".join(
                [
                    f"{item['title']} ({item['domain']})",
                    f"semantic={item['semantic_similarity']}",
                    f"final={item['final_score']}",
                    f"matched={item['matched_skills']}",
                    f"missing={item['missing_skills']}",
                ]
            )
        )
