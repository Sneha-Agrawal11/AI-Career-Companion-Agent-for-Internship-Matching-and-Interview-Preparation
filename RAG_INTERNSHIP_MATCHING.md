# RAG Internship Matching System

## 1. Objective
This module adds a Retrieval-Augmented Generation (RAG) style internship matching flow on top of the existing resume parsing FastAPI project. The goal is to map parsed candidate profiles to the most relevant synthetic internship opportunities.

## 2. Architecture
Flow used in this implementation:

Candidate Resume -> Parsed Structured Data -> Candidate Text -> Embedding -> FAISS Retrieval -> Top K Internships -> Matching Scores -> RAG Explanation

Core components:
- `app/resume_parser.py`: candidate normalization and embedding text preparation
- `app/services/embedding_service.py`: local sentence-transformer embedding model
- `app/services/vector_store.py`: internship loading, FAISS index build/load/search
- `app/services/internship_matcher.py`: semantic + skill + compatibility scoring
- `app/services/rag_service.py`: deterministic explanation generation
- `app/routers/internships.py`: FastAPI endpoints

## 3. Resume Data Preparation
The system does not replace existing parsing APIs. It safely normalizes parsed resume JSON (including partially filled records) into a stable structure with:
- empty list for list fields
- empty string for optional text fields

Supported fields include:
- full_name, email, phone, address, linkedin, github, professional_summary
- skills, technical_skills, soft_skills
- education, work_experience, internships, projects
- certifications, languages, achievements, other_relevant_information

## 4. Internship Dataset
Synthetic internship data is stored at `app/data/internships.json`.

Properties per internship:
- id, title, company, description
- required_skills, preferred_skills
- education_requirements, experience_requirements
- location, work_mode, duration, stipend
- domain, responsibilities, eligibility

Records are intentionally synthetic for project demonstration and include domains like AI/ML, Backend, Data Science, Generative AI, Frontend, Full Stack, DevOps, and others.

## 5. Embedding Model
Local model used:
- `sentence-transformers/all-MiniLM-L6-v2`

No external API is required for core matching.

## 6. FAISS Vector Database
Vector storage path:
- `app/data/vector_store/internships.index`
- `app/data/vector_store/internship_metadata.json`

Index build script:
- `app/data/build_index.py`

The index is built once and reused. It is not rebuilt on every request.

## 7. Semantic Search
The candidate profile text is embedded and searched in FAISS using cosine-like similarity (normalized embeddings with inner product). Top-K nearest internships are returned.

## 8. Matching Score
Final score combines:
- Semantic similarity: 50%
- Skill match percentage: 30%
- Education + experience compatibility: 20%

Formula:

`final_score = (semantic_similarity*100)*0.50 + skill_match*0.30 + compatibility*0.20`

## 9. RAG Pipeline
Retrieved internship records are treated as context. Explanations are generated deterministically from:
- candidate extracted fields
- retrieved internship fields

No internship facts are invented beyond dataset content.

## 10. API Endpoints
New router prefix: `/internships`

- `POST /internships/build-index`
  - JWT protected
  - Builds or rebuilds FAISS index from dataset

- `GET /internships`
  - Lists all available internship records

- `GET /internships/{internship_id}`
  - Returns one internship by id

- `POST /internships/match`
  - JWT protected
  - Accepts candidate structured data directly

- `POST /internships/match/{resume_id}`
  - JWT protected
  - Fetches resume parsed_data from DB and returns top matches
  - supports query param `top_k` (default=5, max=10)

## 11. Testing
Test file:
- `tests/test_internship_matching.py`

Covers multiple candidate profiles including AI/ML, Backend, Data Science, Generative AI, Frontend/Full Stack, Java, Cloud/DevOps, and Data Engineering.

Validation includes:
- top 5 matches available
- semantic score range
- final score range
- matched/missing skill extraction
- domain relevance intersection

## 12. Example Request
`POST /internships/match`

```json
{
  "full_name": "John Doe",
  "skills": ["Python", "SQL", "FastAPI"],
  "education": ["B.Tech Computer Science"],
  "work_experience": ["Backend intern - 1 year"],
  "projects": ["Resume screening API"]
}
```

## 13. Example Response
```json
{
  "candidate": {
    "name": "John Doe",
    "skills": ["Python", "SQL", "FastAPI"]
  },
  "matches": [
    {
      "internship_id": 21,
      "title": "Backend Development Intern - Cohort 1",
      "company": "NeuronNest Labs",
      "domain": "Backend Development",
      "location": "Bengaluru",
      "work_mode": "Remote",
      "duration": "8 weeks",
      "stipend": "INR 12000/month",
      "semantic_similarity": 0.86,
      "skill_match_percentage": 75.0,
      "education_match": 100.0,
      "experience_match": 80.0,
      "final_score": 84.5,
      "matched_skills": ["Python", "FastAPI", "SQL"],
      "missing_skills": ["Git"],
      "reason": "John Doe matches this internship because Python, FastAPI, SQL appear in the resume and align with the internship requirements. Skills that can improve fit: Git. Education compatibility is 100.0% and experience compatibility is 80.0%."
    }
  ]
}
```

## 14. Limitations
- Rule-based compatibility scoring is intentionally simple and can be tuned further.
- Resume fields are only as accurate as upstream extraction quality.
- Synthetic internship data is for educational/demo use only.
- FAISS index must be built before matching endpoints are used.
# RAG Internship Matching System

## 1. Objective
Build a local RAG-based internship matching system on top of the existing FastAPI resume parser project. The system maps extracted resume data to relevant synthetic internship opportunities.

## 2. Architecture
- Resume upload and parsing: existing APIs remain unchanged.
- Candidate normalization: app/resume_parser.py
- Embedding generation: app/services/embedding_service.py
- Vector database (FAISS): app/services/vector_store.py
- Matching and scoring: app/services/internship_matcher.py
- RAG explanation layer: app/services/rag_service.py
- API endpoints: app/routers/internships.py

## 3. Resume Data Preparation
The matching flow consumes parsed resume JSON from the database and normalizes it safely.

Supported fields:
- full_name
- email
- phone
- address
- linkedin
- github
- professional_summary
- skills
- technical_skills
- soft_skills
- education
- work_experience
- internships
- projects
- certifications
- languages
- achievements
- other relevant information

Defensive handling:
- Missing list fields become []
- Missing text fields become ""
- No data is invented

## 4. Internship Dataset
Dataset file: app/data/internships.json

- 60 synthetic internship records
- Realistic structure, clearly marked synthetic in description
- Domains included:
  - AI/ML
  - Machine Learning
  - Data Science
  - Generative AI
  - Backend Development
  - Full Stack Development
  - Frontend Development
  - Python Development
  - Java Development
  - Cloud/DevOps
  - Data Engineering
  - Software Engineering
- Work modes: Remote, Hybrid, On-site

## 5. Embedding Model
Local model:
- sentence-transformers/all-MiniLM-L6-v2

The model is loaded once and reused via a cached singleton for request efficiency.

## 6. FAISS Vector Database
Storage path:
- app/data/vector_store/internships.index
- app/data/vector_store/internship_metadata.json

Index is built offline using:
- app/data/build_index.py

The index is not rebuilt on every request.

## 7. Semantic Search
- Candidate profile is converted to normalized text.
- Text is embedded with sentence-transformers.
- FAISS returns top-k semantically similar internships.

## 8. Matching Score
Final score formula:
- Semantic similarity: 50%
- Skill match percentage: 30%
- Education + experience compatibility: 20%

Formula:
final_score = (semantic_similarity * 100 * 0.50) + (skill_match * 0.30) + (compatibility * 0.20)

Additional metrics:
- matched_skills
n- missing_skills
- skill_match_percentage
- education_match
- experience_match

## 9. RAG Pipeline
Flow:
Candidate resume -> structured candidate data -> candidate embedding -> FAISS retrieval -> top internships as context -> deterministic explanation.

The explanation uses only candidate extracted data and retrieved internship records.

## 10. API Endpoints
Added under router tag Internships:

- POST /internships/build-index
- GET /internships
- GET /internships/{internship_id}
- POST /internships/match
- POST /internships/match/{resume_id}

Matching endpoints are JWT protected using the existing get_current_user dependency.

## 11. Testing
Test file:
- tests/test_internship_matching.py

Contains 8 candidate profiles covering:
- AI/ML
- Backend
- Data Science
- Generative AI
- Frontend/Full Stack
- Java
- Cloud/DevOps
- Data Engineering

Outputs include top 5 matches with semantic score, final score, matched skills, and missing skills.

## 12. Example Request
POST /internships/match

{
  "full_name": "John Doe",
  "skills": ["Python", "FastAPI", "SQL"],
  "education": ["B.Tech Computer Science"],
  "work_experience": ["Backend intern - 1 year"],
  "projects": ["API gateway project"]
}

## 13. Example Response
{
  "candidate": {
    "name": "John Doe",
    "skills": ["Python", "FastAPI", "SQL"]
  },
  "matches": [
    {
      "internship_id": 21,
      "title": "Backend Development Intern - Cohort 1",
      "company": "NeuronNest Labs",
      "domain": "Backend Development",
      "location": "Bengaluru",
      "work_mode": "Remote",
      "duration": "8 weeks",
      "stipend": "INR 12000/month",
      "semantic_similarity": 0.86,
      "skill_match_percentage": 75.0,
      "education_match": 100.0,
      "experience_match": 100.0,
      "final_score": 86.5,
      "matched_skills": ["Python", "FastAPI", "SQL"],
      "missing_skills": ["Git"],
      "reason": "John Doe matches this internship because Python, FastAPI, SQL appear in the resume and align with the internship requirements. Skills that can improve fit: Git. Education compatibility is 100.0% and experience compatibility is 100.0%."
    }
  ]
}

## 14. Limitations
- Matching quality depends on extracted resume text quality.
- Education and experience compatibility are heuristic, not fully semantic.
- No automatic resume-to-user linkage exists for historic resumes with null user_id.
- External LLM explanations are not required; deterministic fallback is used for reliability.
