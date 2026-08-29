"""
Utility functions for resume parsing.

This module provides file reading helpers (PDF, DOCX, TXT), text cleaning,
and regex-based extraction of structured information such as emails, phone
numbers, candidate names, technical skills, education, and work experience.

Dependencies:
    - pdfplumber (recommended PDF reader)
    - PyPDF2 (fallback PDF reader)
    - python-docx (DOCX reader)

All functions are designed to be safe with empty or corrupted inputs and
return empty results instead of raising unhandled exceptions.
"""

import logging
import re
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants / Predefined skill database
# ---------------------------------------------------------------------------

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

# Non-capturing groups so that re.findall returns the COMPLETE phone number
# (including country code) instead of only a captured group.
# Supports common formats such as:
#   +1 (555) 123-4567, +91 98765 43210, 555-123-4567, (555) 123-4567
PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+\d{1,3}[-.\s]?)?"
    r"(?:"
    r"\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}"
    r"|\d{5}[-.\s]?\d{5}"
    r"|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}"
    r")"
    r"(?!\d)"
)

# Matches typical title-cased candidate names (e.g. "John Doe").
NAME_PATTERN = re.compile(r"^[A-Z][a-zA-Z]+(?:[\s'-][A-Z][a-zA-Z]+)+$")

# Lines that should never be treated as a candidate name.
_NAME_EXCLUSIONS = {
    "resume",
    "curriculum vitae",
    "cv",
    "contact",
    "contact details",
    "profile",
    "summary",
    "objective",
    "education",
    "experience",
    "skills",
    "references",
}

SKILLS_DB = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "SQL",
    "React",
    "Node.js",
    "Flask",
    "Django",
    "Spring Boot",
    "Docker",
    "Kubernetes",
    "AWS",
    "Git",
    "MongoDB",
    "PostgreSQL",
    "Redis",
    "TensorFlow",
    "PyTorch",
    "Machine Learning",
    "Deep Learning",
]

EDUCATION_KEYWORDS = [
    "Bachelor",
    "Master",
    "B.Tech",
    "M.Tech",
    "B.E.",
    "MCA",
    "BCA",
    "Computer Science",
    "Engineering",
]

EXPERIENCE_KEYWORDS = [
    "Engineer",
    "Developer",
    "Intern",
    "Analyst",
    "Manager",
]


def _skill_search_pattern(skill: str) -> re.Pattern:
    """
    Build a word-boundary-aware regex pattern for a skill.

    Word boundaries are emulated with lookarounds so that short skills such
    as "C" do not falsely match words like "Computer".

    Args:
        skill: The skill name to search for.

    Returns:
        A compiled case-insensitive regex pattern.
    """
    escaped = re.escape(skill)
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def _read_pdf_fallback(file_path: str) -> str:
    """
    Extract text from a PDF using PyPDF2 as a fallback reader.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text, or an empty string on any failure.
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        logger.error(
            "No PDF reader available. Install pdfplumber or PyPDF2."
        )
        return ""

    try:
        text_parts = []
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:  # noqa: BLE001 - deliberately broad
        logger.warning(
            "Failed to parse PDF '%s' with PyPDF2: %s", file_path, exc
        )
        return ""


def read_file_content(file_path: str) -> str:
    """
    Read text content from a file.

    Supports PDF, DOCX, and plain text files. The file type is determined
    by its extension.

    Args:
        file_path: Path to the file.

    Returns:
        Extracted text content as a string. Returns an empty string when
        the file is missing, unreadable, or corrupted.

    Raises:
        ValueError: If the file extension is not supported.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return read_pdf(str(path))
    if ext == ".docx":
        return read_docx(str(path))
    if ext == ".txt":
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logger.warning("Failed to read TXT file '%s': %s", file_path, exc)
            return ""

    raise ValueError(f"Unsupported file format: {ext or 'no extension'}")


def read_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Uses pdfplumber when available and falls back to PyPDF2. Corrupted or
    unreadable PDFs return an empty string instead of raising an error.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text, or an empty string on failure.
    """
    return extract_text_from_pdf(file_path)


def read_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file using python-docx.

    Includes text from both paragraphs and tables (tables are commonly used
    in resumes). Corrupted or unreadable files return an empty string.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Extracted text, or an empty string on failure.
    """
    try:
        from docx import Document
    except ImportError:
        logger.error("python-docx is not installed.")
        return ""

    try:
        document = Document(file_path)
        text_parts = [paragraph.text for paragraph in document.paragraphs]

        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        text_parts.append(cell.text)

        return "\n".join(text_parts)
    except Exception as exc:  # noqa: BLE001 - deliberately broad
        logger.warning(
            "Failed to read DOCX file '%s': %s", file_path, exc
        )
        return ""


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted resume text.

    Removes null characters, collapses multiple spaces and blank lines,
    trims whitespace around line breaks, and strips surrounding whitespace.

    Args:
        text: Raw text to clean.

    Returns:
        Cleaned text. Returns an empty string if input is empty.
    """
    if not text:
        return ""

    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using pdfplumber.

    This is the primary PDF extraction function used by the API router.
    It is safe for missing or corrupted PDFs and returns an empty string
    in such cases instead of crashing.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text, or an empty string on any failure.
    """
    if not pdf_path:
        logger.warning("PDF path is empty.")
        return ""

    path = Path(pdf_path)
    if not path.exists():
        logger.warning("PDF file not found: %s", pdf_path)
        return ""

    try:
        import pdfplumber
    except ImportError:
        logger.warning("pdfplumber not installed. Falling back to PyPDF2.")
        return _read_pdf_fallback(pdf_path)

    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:  # noqa: BLE001 - deliberately broad
        logger.warning(
            "Failed to parse PDF '%s' with pdfplumber: %s", pdf_path, exc
        )
        logger.warning("Trying PyPDF2 fallback...")
        return _read_pdf_fallback(pdf_path)


def extract_emails(text: str) -> list[str]:
    """
    Extract email addresses from text using regex.

    Duplicate emails are removed while preserving order of first occurrence.

    Args:
        text: Input text.

    Returns:
        List of unique email addresses found.
    """
    if not text:
        return []

    matches = re.findall(EMAIL_PATTERN, text)
    return list(dict.fromkeys(matches))


def extract_phone_numbers(text: str) -> list[str]:
    """
    Extract complete phone numbers from text using regex.

    Returns the full phone number including country code when present,
    not just a captured group. Duplicate numbers are removed.

    Args:
        text: Input text.

    Returns:
        List of unique phone numbers found.
    """
    if not text:
        return []

    matches = re.findall(PHONE_PATTERN, text)
    return list(dict.fromkeys(matches))


def extract_name(text: str) -> Optional[str]:
    """
    Extract the candidate's name from the beginning of the resume.

    Scans the first few non-empty lines for a title-cased name and skips
    lines that look like headers, contact details, or contain digits/email
    addresses.

    Args:
        text: Resume text.

    Returns:
        The candidate's name, or None if no name could be detected.
    """
    if not text or not text.strip():
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 1) All-caps names (e.g. "JOHN DOE", "MARY JANE SMITH").
    for line in lines[:6]:
        if len(line) > 40:
            continue
        if _looks_like_non_name_line(line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4:
            if line.isupper() and all(word.isalpha() for word in words):
                return line.title()

    # 2) Strict title-case pattern (e.g. "John Doe", "Mary-Jane Smith").
    for line in lines[:6]:
        if len(line) > 40:
            continue
        if _looks_like_non_name_line(line):
            continue
        if NAME_PATTERN.match(line):
            return line

    # 3) Fallback: 2-4 words, each capitalized, no digits/symbols.
    for line in lines[:6]:
        if len(line) > 40:
            continue
        if _looks_like_non_name_line(line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(word[:1].isupper() for word in words):
                return line

    return None


def _looks_like_non_name_line(line: str) -> bool:
    """
    Determine whether a line is unlikely to be a person's name.

    A line is treated as non-name if it contains digits, an email address,
    a URL, phone-like characters, or matches known header/section words.

    Args:
        line: A single stripped text line.

    Returns:
        True if the line should be excluded from name detection.
    """
    lower = line.lower()
    if lower in _NAME_EXCLUSIONS:
        return True
    if re.search(r"[\d@]|https?://|www\.", line, re.IGNORECASE):
        return True
    if re.search(r"\(\d{3}\)", line):
        return True
    if any(header in lower for header in _NAME_EXCLUSIONS):
        return True
    return False


def extract_skills(text: str) -> list[str]:
    """
    Extract technical skills from text using a predefined skill database.

    Matching is case-insensitive and word-boundary aware so short skills
    such as "C" do not produce false positives inside other words.

    Args:
        text: Resume text.

    Returns:
        List of unique skills found, in database order of appearance.
    """
    if not text:
        return []

    found: list[str] = []
    for skill in SKILLS_DB:
        if _skill_search_pattern(skill).search(text):
            found.append(skill)

    return list(dict.fromkeys(found))


def extract_education(text: str) -> list[str]:
    """
    Extract education-related lines from text.

    A line is considered educational if it contains any of the predefined
    education keywords such as Bachelor, Master, B.Tech, M.Tech, B.E.,
    MCA, BCA, Computer Science, or Engineering.

    Args:
        text: Resume text.

    Returns:
        List of unique education lines found.
    """
    if not text:
        return []

    education: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lower_line = line.lower()
        for keyword in EDUCATION_KEYWORDS:
            if keyword.lower() in lower_line:
                education.append(line)
                break

    return list(dict.fromkeys(education))


def extract_experience(text: str) -> list[str]:
    """
    Extract work-experience / job-title lines from text.

    A line is considered experience-related if it contains any of the
    predefined keywords such as Engineer, Developer, Intern, Analyst, or
    Manager.

    Args:
        text: Resume text.

    Returns:
        List of unique experience lines found.
    """
    if not text:
        return []

    experience: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lower_line = line.lower()
        for keyword in EXPERIENCE_KEYWORDS:
            if keyword.lower() in lower_line:
                experience.append(line)
                break

    return list(dict.fromkeys(experience))

def analyze_resume(text):
    score = 0
    strengths = []
    weaknesses = []
    suggestions = []

    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    emails = extract_emails(text)
    phones = extract_phone_numbers(text)
    name = extract_name(text)

    # 1. Contact info (30 points max)
    if name:
        score += 10
        strengths.append("Name detected")
    else:
        weaknesses.append("Name missing")

    if emails:
        score += 10
        strengths.append("Email detected")
    else:
        weaknesses.append("Email missing")

    if phones:
        score += 10
        strengths.append("Phone number detected")
    else:
        weaknesses.append("Phone number missing")

    # 2. Skills (25 points max)
    if skills:
        num_skills = len(skills)
        skill_score = min(25, num_skills * 3)
        score += skill_score
        strengths.append(f"Technical skills found ({num_skills})")
    else:
        weaknesses.append("No technical skills found")

    # 3. Education (15 points max)
    if education:
        edu_score = min(15, len(education) * 5 + 5)
        score += edu_score
        strengths.append("Education section found")
    else:
        weaknesses.append("Education section missing")

    # 4. Experience (20 points max)
    if experience:
        exp_score = min(20, len(experience) * 4 + 5)
        score += exp_score
        strengths.append("Work experience found")
    else:
        weaknesses.append("Work experience missing")

    # 5. Length / Detail (10 points max)
    text_len = len(text.strip()) if text else 0
    if text_len > 1500:
        score += 10
    elif text_len > 1000:
        score += 7
    elif text_len > 500:
        score += 4
    elif text_len > 0:
        score += 2

    if score < 70:
        suggestions.append("Add more technical skills")
        suggestions.append("Include projects")
        suggestions.append("Add certifications")
    elif score < 90:
        suggestions.append("Improve resume summary")
        suggestions.append("Add measurable achievements")
    else:
        suggestions.append("Excellent resume")

    return {
        "resume_score": min(100, max(0, score)),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }