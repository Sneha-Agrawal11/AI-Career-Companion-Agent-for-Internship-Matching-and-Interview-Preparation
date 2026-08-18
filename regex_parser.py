"""
Regex-based resume parser.
Extracts structured information from resume text using regular expressions.
"""

import re
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ParsedResume:
    """Data class for parsed resume information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    experience: list[dict] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    summary: Optional[str] = None


# Common skill keywords for detection
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
    "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "redis",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
    "git", "linux", "rest", "graphql", "html", "css", "sass", "less",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "agile", "scrum", "jira", "confluence", "ci/cd", "devops", "mlops",
    "tableau", "power bi", "excel", "spreadsheet", "data analysis",
    "communication", "leadership", "teamwork", "problem solving",
]


class RegexParser:
    """
    Parses resume text using regex patterns to extract structured information.
    """

    def __init__(self):
        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.phone_pattern = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
        self.name_pattern = re.compile(
            r"^(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$",
            re.MULTILINE
        )
        self.education_section_pattern = re.compile(
            r"(?:education|academic|academic background|educational qualification)[\s:]*(.*?)(?=\n\s*\n(?:[A-Z]|\d)|$)",
            re.IGNORECASE | re.DOTALL
        )
        self.experience_section_pattern = re.compile(
            r"(?:experience|work experience|professional experience|employment|work history)[\s:]*(.*?)(?=\n\s*\n(?:[A-Z]|\d)|$)",
            re.IGNORECASE | re.DOTALL
        )
        self.skills_section_pattern = re.compile(
            r"(?:skills|technical skills|core competencies|technologies)[\s:]*(.*?)(?=\n\s*\n(?:[A-Z]|\d)|$)",
            re.IGNORECASE | re.DOTALL
        )
        self.certification_pattern = re.compile(
            r"(?:certification|certifications|certified)[\s:]*(.*?)(?=\n\s*\n(?:[A-Z]|\d)|$)",
            re.IGNORECASE | re.DOTALL
        )

    def parse(self, text: str) -> ParsedResume:
        """
        Parse resume text and return structured data.

        Args:
            text: Raw resume text.

        Returns:
            ParsedResume object with extracted information.
        """
        resume = ParsedResume()
        resume.email = self._extract_email(text)
        resume.phone = self._extract_phone(text)
        resume.name = self._extract_name(text)
        resume.skills = self._extract_skills(text)
        resume.education = self._extract_education(text)
        resume.experience = self._extract_experience(text)
        resume.certifications = self._extract_certifications(text)
        resume.summary = self._extract_summary(text)
        return resume

    def _extract_email(self, text: str) -> Optional[str]:
        match = self.email_pattern.search(text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        match = self.phone_pattern.search(text)
        return match.group(0) if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        lines = text.strip().split("\n")
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if self.name_pattern.match(line):
                return line
        return None

    def _extract_skills(self, text: str) -> list[str]:
        found_skills = []
        text_lower = text.lower()

        for skill in COMMON_SKILLS:
            if skill in text_lower:
                found_skills.append(skill)

        # Also check for a dedicated skills section
        section_match = self.skills_section_pattern.search(text)
        if section_match:
            section_text = section_match.group(1).lower()
            for skill in COMMON_SKILLS:
                if skill in section_text and skill not in found_skills:
                    found_skills.append(skill)

        return found_skills

    def _extract_education(self, text: str) -> list[dict]:
        education_entries = []
        section_match = self.education_section_pattern.search(text)
        if section_match:
            section_text = section_match.group(1)
            entries = re.split(r"\n\s*\n", section_text.strip())
            for entry in entries:
                entry = entry.strip()
                if entry:
                    education_entries.append({"raw": entry})
        return education_entries

    def _extract_experience(self, text: str) -> list[dict]:
        experience_entries = []
        section_match = self.experience_section_pattern.search(text)
        if section_match:
            section_text = section_match.group(1)
            entries = re.split(r"\n\s*\n", section_text.strip())
            for entry in entries:
                entry = entry.strip()
                if entry:
                    # Try to extract date range, company, and role
                    date_pattern = r"(\d{4}\s*(?:-|–|to)\s*(?:\d{4}|present|current))"
                    dates = re.findall(date_pattern, entry, re.IGNORECASE)
                    experience_entries.append({
                        "raw": entry,
                        "dates": dates,
                    })
        return experience_entries

    def _extract_certifications(self, text: str) -> list[str]:
        certs = []
        section_match = self.certification_pattern.search(text)
        if section_match:
            section_text = section_match.group(1)
            entries = re.split(r"\n\s*\n", section_text.strip())
            for entry in entries:
                entry = entry.strip()
                if entry:
                    certs.append(entry)
        return certs

    def _extract_summary(self, text: str) -> Optional[str]:
        summary_pattern = re.compile(
            r"(?:summary|professional summary|profile|about me)[\s:]*(.*?)(?=\n\s*\n(?:[A-Z]|\d)|$)",
            re.IGNORECASE | re.DOTALL
        )
        match = summary_pattern.search(text)
        if match:
            summary = match.group(1).strip()
            return summary if summary else None
        return None


def parse_resume(text: str) -> dict:
    """
    Convenience function to parse resume text using regex parser.

    Args:
        text: Raw resume text.

    Returns:
        Dictionary with parsed resume data.
    """
    parser = RegexParser()
    result = parser.parse(text)
    return asdict(result)
