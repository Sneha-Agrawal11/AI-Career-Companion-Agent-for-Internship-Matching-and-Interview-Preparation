"""
LLM-based resume parser.
Uses OpenAI's GPT models to extract structured information from resume text.
"""

import json
import logging
from typing import Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class LLMParsedResume:
    """Data class for LLM-parsed resume information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    experience: list[dict] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    summary: Optional[str] = None
    projects: list[dict] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)


class LLMParser:
    """
    Parses resume text using an LLM (e.g., OpenAI GPT) to extract
    structured information with higher accuracy than regex.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-oss-120b"):
        """
        Initialize the LLM parser.

        Args:
            api_key: OpenAI API key. If None, tries to read from env.
            model: The model to use for parsing.
        """
        self.model = model
        self._setup_client(api_key)

    def _setup_client(self, api_key: Optional[str] = None):
        """Set up the OpenAI client."""
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            self._available = True
        except ImportError:
            logger.warning(
                "OpenAI package not installed. LLM parser will not be available. "
                "Install with: pip install groq"
            )
            self._available = False
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if the LLM parser is available for use."""
        return self._available

    def parse(self, text: str) -> LLMParsedResume:
        """
        Parse resume text using the LLM.

        Args:
            text: Raw resume text.

        Returns:
            LLMParsedResume object with extracted information.
        """
        if not self._available:
            logger.error("LLM parser is not available. Check API key and installation.")
            return LLMParsedResume()

        prompt = self._build_prompt(text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a resume parsing assistant. Extract structured information "
                            "from the resume text provided. Return ONLY valid JSON without any "
                            "markdown formatting or code blocks."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            raw_response = response.choices[0].message.content.strip()
            return self._parse_response(raw_response)

        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return LLMParsedResume()

    def _build_prompt(self, text: str) -> str:
        """Build the prompt for the LLM."""
        return f"""
Extract structured information from the following resume text. Return a JSON object with these fields:
- name: Full name of the candidate
- email: Email address
- phone: Phone number
- skills: List of technical and soft skills
- education: List of education entries, each with institution, degree, field, dates
- experience: List of work experience entries, each with company, role, dates, description
- certifications: List of certifications
- summary: Professional summary or objective
- projects: List of notable projects, each with name, description, technologies
- languages: List of languages known

Resume Text:
---
{text}
---
"""

    def _parse_response(self, response: str) -> LLMParsedResume:
        """Parse the LLM response JSON into a structured object."""
        # Try to extract JSON from the response (in case of markdown wrapping)
        try:
            # Find JSON boundaries
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
            else:
                data = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return LLMParsedResume()

        return LLMParsedResume(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            skills=data.get("skills", []),
            education=data.get("education", []),
            experience=data.get("experience", []),
            certifications=data.get("certifications", []),
            summary=data.get("summary"),
            projects=data.get("projects", []),
            languages=data.get("languages", []),
        )


def parse_resume_with_llm(
    text: str,
    api_key: Optional[str] = None,
    model: str = "openai/gpt-oss-120b"
) -> dict:
    """
    Convenience function to parse resume text using LLM.

    Args:
        text: Raw resume text.
        api_key: OpenAI API key.
        model: Model to use.

    Returns:
        Dictionary with parsed resume data.
    """
    parser = LLMParser(api_key=api_key, model=model)
    result = parser.parse(text)
    return asdict(result)
