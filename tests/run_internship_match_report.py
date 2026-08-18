"""Run internship matching endpoint test cases and generate a markdown report."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app

REPORT_FILE = Path("tests/internship_matching_test_report.md")

TEST_CASES: list[dict[str, Any]] = [
    {
        "name": "1. AI/ML",
        "payload": {
            "full_name": "Aarav Mehta",
            "professional_summary": "AI/ML enthusiast with model building and experimentation experience.",
            "skills": ["Python", "Machine Learning", "NumPy", "Pandas", "Scikit-learn"],
            "technical_skills": ["TensorFlow", "PyTorch", "Model Evaluation"],
            "education": ["B.Tech Computer Science"],
            "work_experience": ["ML Intern - 1 year"],
            "projects": ["Image classification model for plant disease detection"],
            "certifications": ["Machine Learning Specialization"],
        },
    },
    {
        "name": "2. Backend Development",
        "payload": {
            "full_name": "Neha Sharma",
            "professional_summary": "Backend developer focused on API design and service reliability.",
            "skills": ["Python", "FastAPI", "SQL", "Git", "Docker"],
            "technical_skills": ["REST API Design", "Redis", "PostgreSQL"],
            "education": ["B.E. Information Technology"],
            "work_experience": ["Backend Intern - 8 months"],
            "projects": ["Order management microservice"],
        },
    },
    {
        "name": "3. Data Science",
        "payload": {
            "full_name": "Kritika Rao",
            "professional_summary": "Data science learner with analytics and visualization skills.",
            "skills": ["Python", "SQL", "Pandas", "Data Visualization", "Statistics"],
            "technical_skills": ["Power BI", "A/B Testing", "Scikit-learn"],
            "education": ["B.Sc Data Science"],
            "work_experience": ["Data Analyst Intern - 1 year"],
            "projects": ["Customer churn analysis dashboard"],
        },
    },
    {
        "name": "4. Generative AI",
        "payload": {
            "full_name": "Rahul Singh",
            "professional_summary": "Worked on LLM applications and retrieval-augmented systems.",
            "skills": ["Python", "LLM Fundamentals", "Prompt Engineering", "APIs", "RAG"],
            "technical_skills": ["LangChain", "Vector Databases", "FastAPI"],
            "education": ["B.Tech AI and Data Science"],
            "work_experience": ["GenAI Intern - 6 months"],
            "projects": ["Knowledge-base chatbot with retrieval"],
        },
    },
    {
        "name": "5. Frontend/Web Development",
        "payload": {
            "full_name": "Isha Kapoor",
            "professional_summary": "Frontend-focused developer building responsive web apps.",
            "skills": ["JavaScript", "React", "HTML", "CSS", "Node.js"],
            "technical_skills": ["TypeScript", "Next.js", "Accessibility"],
            "education": ["BCA"],
            "work_experience": ["Frontend Intern - 1 year"],
            "projects": ["E-commerce UI with React"],
        },
    },
    {
        "name": "6. Education-Focused Matching",
        "payload": {
            "full_name": "Priya Nair",
            "professional_summary": "Final-year student with strong academic foundation and moderate practical exposure.",
            "skills": ["Python", "SQL", "Git"],
            "technical_skills": ["Data Structures", "Algorithms"],
            "education": ["Final year undergraduate in Computer Science", "B.Tech Computer Science"],
            "work_experience": ["Academic project contributor"],
            "projects": ["Campus event management web application"],
        },
    },
    {
        "name": "7. Experience-Focused Matching",
        "payload": {
            "full_name": "Vikram Malhotra",
            "professional_summary": "Hands-on candidate with practical engineering internship experience.",
            "skills": ["Python", "SQL", "ETL", "Data Modeling", "Airflow"],
            "technical_skills": ["AWS", "CI/CD", "Docker"],
            "education": ["Bachelor's degree in Engineering"],
            "work_experience": ["Data Engineering Intern - 2 years", "Backend Intern - 1 year"],
            "projects": ["Cloud ETL pipeline with scheduling"],
        },
    },
    {
        "name": "8. Multiple Skill/Project-Based Matching",
        "payload": {
            "full_name": "Sana Fatima",
            "professional_summary": "Cross-domain candidate combining backend, cloud, and AI projects.",
            "skills": [
                "Python",
                "FastAPI",
                "Machine Learning",
                "Docker",
                "AWS",
                "SQL",
                "React",
            ],
            "technical_skills": ["TensorFlow", "CI/CD", "REST API Design", "Kubernetes"],
            "education": ["B.Tech Computer Engineering"],
            "work_experience": ["Software Intern - 1.5 years"],
            "projects": [
                "RAG resume screener",
                "Cloud-hosted backend API",
                "ML model deployment pipeline",
            ],
            "certifications": ["AWS Cloud Practitioner", "Deep Learning Fundamentals"],
        },
    },
]


def _ensure_user_and_get_token(client: TestClient, email: str, password: str) -> str:
    register_payload = {
        "full_name": "Endpoint Test User",
        "email": email,
        "password": password,
        "role": "candidate",
    }
    client.post("/auth/register", json=register_payload)

    token_resp = client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    token_resp.raise_for_status()
    return token_resp.json()["access_token"]


def _format_match_row(match: dict[str, Any]) -> str:
    return (
        f"| {match.get('internship_id')} | {match.get('title')} | {match.get('company')}"
        f" | {match.get('domain')} | {match.get('semantic_similarity')}"
        f" | {match.get('final_score')} | {match.get('skill_match_percentage')}"
        f" | {', '.join(match.get('matched_skills', []))}"
        f" | {', '.join(match.get('missing_skills', []))} |"
    )


def run() -> None:
    client = TestClient(app)

    email = "internship.endpoint.tests@gmail.com"
    password = "TestPass123"
    token = _ensure_user_and_get_token(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    build_resp = client.post("/internships/build-index", headers=headers)
    build_resp.raise_for_status()

    report_lines: list[str] = []
    report_lines.append("# Internship Matching Endpoint Test Report")
    report_lines.append("")
    report_lines.append(f"Generated on: {datetime.now().isoformat()}")
    report_lines.append("")
    report_lines.append("Endpoint under test: POST /internships/match?top_k=5")
    report_lines.append("")

    for case in TEST_CASES:
        response = client.post(
            "/internships/match?top_k=5",
            json=case["payload"],
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        matches = data.get("matches", [])

        report_lines.append(f"## {case['name']}")
        report_lines.append("")
        report_lines.append("Candidate payload summary:")
        report_lines.append("")
        report_lines.append(f"- Name: {case['payload'].get('full_name', '')}")
        report_lines.append(
            "- Skills: " + ", ".join(case["payload"].get("skills", []))
        )
        report_lines.append(
            "- Education: " + " | ".join(case["payload"].get("education", []))
        )
        report_lines.append(
            "- Experience: " + " | ".join(case["payload"].get("work_experience", []))
        )
        report_lines.append("")
        report_lines.append("Top matches returned:")
        report_lines.append("")
        report_lines.append(
            "| Internship ID | Title | Company | Domain | Semantic Similarity | Final Score | Skill Match % | Matched Skills | Missing Skills |"
        )
        report_lines.append(
            "|---|---|---|---|---:|---:|---:|---|---|"
        )

        for match in matches:
            report_lines.append(_format_match_row(match))

        report_lines.append("")

    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report written to {REPORT_FILE}")


if __name__ == "__main__":
    run()
