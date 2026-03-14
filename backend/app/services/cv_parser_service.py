import asyncio
import json
import logging
import re

import anthropic
import pdfplumber

from app.core.config import settings
from app.schemas.applicant import CVExtractedData

logger = logging.getLogger(__name__)

# Prompt sent to Claude for structured CV extraction
_EXTRACTION_PROMPT = """Extract the following information from the CV text below and return ONLY a valid JSON object with these exact keys:
- "skills": a list of technical and professional skills (strings)
- "roles": a list of job titles / roles the person has held (strings)
- "contact_info": a dict with keys "name", "email", "phone" (use empty string if not found)

CV text:
{cv_text}

Return only the JSON object, no additional text."""

# Maximum characters sent to Claude to stay within token limits
_MAX_TEXT_CHARS = 8000

# Score weight per skill found
_SCORE_PER_SKILL = 5
_MAX_SCORE = 100.0


def _extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from all pages of a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _fallback_extraction(raw_text: str) -> CVExtractedData:
    """Regex-based fallback when Anthropic API key is not configured."""
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", raw_text)
    phone_match = re.search(r"[\+\(]?[\d\s\-\(\)]{7,20}", raw_text)
    name_match = re.match(r"^([A-ZÄÖÜ][a-zäöüß]+(?:\s[A-ZÄÖÜ][a-zäöüß]+)+)", raw_text.strip())

    contact_info: dict[str, str] = {
        "name": name_match.group(1) if name_match else "",
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0).strip() if phone_match else "",
    }

    # Extract simple skill indicators: capitalized words or known tech keywords
    skill_pattern = re.compile(
        r"\b(Python|Java|JavaScript|TypeScript|SQL|Docker|Kubernetes|AWS|Azure|GCP|"
        r"React|Vue|Angular|FastAPI|Django|PostgreSQL|MongoDB|Redis|Git|CI/CD)\b",
        re.IGNORECASE,
    )
    skills = list({m.group(0) for m in skill_pattern.finditer(raw_text)})

    return CVExtractedData(skills=skills, roles=[], contact_info=contact_info)


def _call_claude_api(raw_text: str) -> CVExtractedData:
    """Call Anthropic Claude API to extract structured CV data."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = _EXTRACTION_PROMPT.format(cv_text=raw_text[:_MAX_TEXT_CHARS])

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_json = message.content[0].text.strip()
    # Strip possible markdown code fences before parsing
    cleaned_json = re.sub(r"```(?:json)?|```", "", raw_json).strip()
    try:
        data = json.loads(cleaned_json)
    except json.JSONDecodeError as exc:
        logger.warning("Claude returned unparseable JSON: %s", exc)
        raise

    return CVExtractedData(
        skills=data.get("skills", []),
        roles=data.get("roles", []),
        contact_info=data.get("contact_info", {}),
    )


def _calculate_score(extracted: CVExtractedData) -> float:
    """Simple heuristic: 5 points per skill, capped at 100."""
    return min(len(extracted.skills) * _SCORE_PER_SKILL, _MAX_SCORE)


async def parse_cv(file_path: str) -> tuple[str, CVExtractedData, float]:
    """Parse a CV PDF and return (raw_text, extracted_data, matching_score).

    Falls back to regex extraction when ANTHROPIC_API_KEY is not set.
    Never raises – returns empty CVExtractedData on unrecoverable errors.
    """
    try:
        raw_text = await asyncio.to_thread(_extract_text_from_pdf, file_path)
    except Exception as exc:
        logger.error("PDF text extraction failed for %s: %s", file_path, exc)
        empty = CVExtractedData(skills=[], roles=[], contact_info={})
        return "", empty, 0.0

    try:
        if settings.ANTHROPIC_API_KEY:
            extracted = await asyncio.to_thread(_call_claude_api, raw_text)
        else:
            logger.info("ANTHROPIC_API_KEY not set – using regex fallback extraction")
            extracted = await asyncio.to_thread(_fallback_extraction, raw_text)
    except Exception as exc:
        logger.error("CV data extraction failed: %s", exc)
        extracted = await asyncio.to_thread(_fallback_extraction, raw_text)

    score = _calculate_score(extracted)
    return raw_text, extracted, score
