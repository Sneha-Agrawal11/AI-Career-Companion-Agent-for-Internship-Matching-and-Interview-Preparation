from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    name: str | None = None
    full_name: str | None = None
    email: EmailStr
    password: str
    role: str = "student"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: str


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    parsed_data: str

class ResumeCreate(BaseModel):
    filename: str
    parsed_data: str


class CandidateInput(BaseModel):
    full_name: str | None = ""
    email: str | None = ""
    phone: str | None = ""
    address: str | None = ""
    linkedin: str | None = ""
    github: str | None = ""
    professional_summary: str | None = ""
    skills: list[str] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    work_experience: list[str] = Field(default_factory=list)
    internships: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    other_relevant_information: list[str] = Field(default_factory=list)


class InternshipMatchItem(BaseModel):
    internship_id: int
    title: str
    company: str
    domain: str
    location: str
    work_mode: str
    duration: str
    stipend: str
    semantic_similarity: float
    skill_match_percentage: float
    education_match: float
    experience_match: float
    final_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reason: str


class InternshipMatchResponse(BaseModel):
    candidate: dict
    matches: list[InternshipMatchItem]


class InternshipListResponse(BaseModel):
    total: int
    internships: list[dict]


from datetime import datetime

class ChatSessionCreate(BaseModel):
    title: str | None = "New Chat"

class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    agent_type: str | None = "product"
    created_at: datetime
    updated_at: datetime

class ChatMessageCreate(BaseModel):
    message: str
    internship_id: int | None = None
    include_resume: bool = True

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    role: str
    message: str
    created_at: datetime