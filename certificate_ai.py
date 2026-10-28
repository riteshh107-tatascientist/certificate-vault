
"""Certificate text extraction and improved metadata suggestions."""

from datetime import date, datetime
import io
import re

import fitz
from PIL import Image
import pytesseract


# Keep these labels compatible with the categories configured in app.py.
CATEGORY_RULES = [
    ("Hackathon", ["hackathon", "hack fest", "innovation challenge"]),
    ("Quiz Competition", ["quiz competition", "tech quiz", "quiz contest"]),
    ("Coding Competition", ["coding competition", "coding contest", "programming contest"]),
    ("Workshop", ["workshop", "hands-on workshop"]),
    ("Webinar & Seminar", ["webinar", "seminar", "guest lecture"]),
    ("Bootcamp & Training", ["bootcamp", "training program", "training programme"]),
    ("Internship", ["internship", "intern"]),
    ("Job Simulation", ["job simulation", "virtual experience program"]),
    ("AI & Machine Learning", ["artificial intelligence", "machine learning", "deep learning", "generative ai"]),
    ("Data Science & Analytics", ["data science", "data analytics", "data analysis"]),
    ("Programming & Software Development", ["python programming", "java programming", "software development"]),
    ("Course Completion", ["course completion", "successfully completed", "completion certificate"]),
    ("Academic Achievement", ["academic achievement", "academic excellence"]),
    ("Award & Recognition", ["winner", "first prize", "second prize", "award of excellence"]),
    ("Volunteering & Leadership", ["volunteer", "leadership", "community service"]),
]

SKILL_KEYWORDS = [
    "Python", "Java", "C++", "SQL", "Machine Learning",
    "Deep Learning", "Artificial Intelligence", "Data Science",
    "Data Analytics", "Power BI", "Tableau", "Excel",
    "Statistics", "Generative AI", "NLP", "Computer Vision",
    "Git", "GitHub", "Cloud Computing", "Cybersecurity",
    "Web Development", "HTML", "CSS", "JavaScript",
    "Communication", "Leadership", "Problem Solving",
    "Critical Thinking", "Teamwork", "Research",
]

BAD_TITLE_PHRASES = [
    "certificate no", "certificate number", "certificate id",
    "credential id", "serial number", "registration number",
    "this is to certify", "has successfully", "successfully completed",
    "awarded to", "presented to", "date of issue",
    "father name", "father's name", "son of", "daughter of",
]

BAD_ISSUER_PHRASES = [
    "successfully", "has successfully", "this is to certify",
    "certificate no", "certificate number", "certificate id",
    "awarded to", "presented to", "has completed",
    "father name", "son of", "daughter of",
]


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" \t:|-•")


def get_lines(text: str) -> list[str]:
    return [clean_line(line) for line in text.splitlines() if clean_line(line)]


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract embedded PDF text or OCR text from a PDF/image."""
    if filename.lower().endswith(".pdf"):
        with fitz.open(stream=file_bytes, filetype="pdf") as document:
            pages = list(document)
            embedded = "\n".join(page.get_text("text") for page in pages[:5])

            if len(embedded.strip()) >= 40:
                return embedded[:30000]

            # Scanned PDF: OCR first three pages.
            parts = []
            for page in pages[:3]:
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )
                image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                parts.append(pytesseract.image_to_string(image))

            return "\n".join(parts)[:30000]

    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return pytesseract.image_to_string(image)[:30000]


def detect_credential_id(text: str) -> str:
    """Find labelled IDs, including formats such as BCT/2026/505181."""
    patterns = [
        r"(?:certificate\s*(?:no\.?|number|id)|credential\s*id|"
        r"certification\s*id|serial\s*(?:no\.?|number))"
        r"\s*[:#\-]?\s*([A-Z0-9][A-Z0-9/_\-]{2,})",
        r"\b([A-Z]{2,}[/-]\d{4}[/-]\d{3,})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = match.group(1).strip(" .,:;")
            # Reject common OCR words accidentally captured as IDs.
            if value.lower() not in {"successfully", "completed", "participation"}:
                return value[:100]

    return ""


def detect_title(text: str, filename: str) -> str:
    """Prefer meaningful certificate headings, not IDs or body text."""
    lines = get_lines(text)

    # Prefer explicit certificate/award titles.
    for line in lines[:40]:
        lower = line.lower()

        if any(bad in lower for bad in BAD_TITLE_PHRASES):
            continue
        if re.search(r"\b(?:no\.?|number|id)\s*[:#]?\s*[A-Z0-9/_-]{4,}", line, re.I):
            continue
        if re.fullmatch(r"[\W\d_]+", line):
            continue

        title_patterns = [
            r"certificate of (?:participation|completion|achievement|appreciation|excellence|attendance)",
            r"(?:hackathon|quiz competition|coding competition|workshop|internship|bootcamp)",
            r"(?:award of|certificate in|course on|training in)",
        ]

        if any(re.search(pattern, lower) for pattern in title_patterns):
            return line[:100]

    # Look for a meaningful short heading near the beginning.
    for line in lines[:15]:
        lower = line.lower()
        if any(bad in lower for bad in BAD_TITLE_PHRASES):
            continue
        if len(line) < 5 or len(line) > 75:
            continue
        if re.search(r"\b(?:20\d{2}|BCT/)\b", line, re.I):
            continue
        if lower in {"certificate", "congratulations", "successfully", "has"}:
            continue
        if re.search(r"\b(?:father|mother|son of|daughter of)\b", lower):
            continue

        # Avoid picking up a complete sentence as a heading.
        if len(line.split()) <= 9 and not line.endswith("."):
            return line

    filename_title = re.sub(r"\.[^.]+$", "", filename)
    filename_title = re.sub(r"[_-]+", " ", filename_title).strip()

    if filename_title and filename_title.lower() not in {
        "certificate", "certificate pdf", "document", "scan"
    }:
        return filename_title[:100]

    return "Certificate of Achievement"


def detect_recipient(text: str) -> str:
    """Extract only the likely recipient name, stopping at extra details."""
    patterns = [
        r"(?:this is to certify that|awarded to|presented to|"
        r"certify that|participant name|student name|recipient)"
        r"\s*[:\-]?\s*(.{3,100})",
    ]

    stop_words = re.compile(
        r"\b(?:has|have|had|father|mother|son of|daughter of|"
        r"for successfully|successfully|who has|date|certificate no)\b",
        re.IGNORECASE,
    )

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue

        candidate = clean_line(match.group(1))
        candidate = re.split(r"[\r\n]", candidate)[0]
        candidate = stop_words.split(candidate)[0]
        candidate = clean_line(candidate)

        # Reject overly long OCR results instead of showing misleading names.
        if 3 <= len(candidate) <= 60 and len(candidate.split()) <= 6:
            return candidate

    return ""


def detect_issuer(text: str) -> str:
    """Return a plausible organization name; leave uncertain results blank."""
    lines = get_lines(text)

    organization_words = (
        "university", "institute", "college", "technologies", "technology",
        "foundation", "academy", "corporation", "limited", "ltd",
        "private", "pvt", "company", "department", "council",
        "association", "society", "school", "laboratory", "labs",
        "ibm", "google", "microsoft", "tata", "forage", "coursera",
        "udemy", "nptel", "iit ", "iit-", "government",
    )

    for line in lines[:30]:
        lower = line.lower()

        if any(bad in lower for bad in BAD_ISSUER_PHRASES):
            continue
        if len(line) < 4 or len(line) > 100:
            continue
        if re.search(r"\b(?:20\d{2}|BCT/)\b", line, re.I):
            continue
        if re.search(r"\b(?:father|mother|son of|daughter of)\b", lower):
            continue
        if re.search(r"\b(?:certificate|participation|successfully|completed)\b", lower):
            continue

        if any(word in lower for word in organization_words):
            return line[:100]

    # Do not invent an issuer when the text does not identify one reliably.
    return ""


def detect_date(text: str) -> date:
    patterns = [
        (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
         ["%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]),
        (r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
         ["%Y-%m-%d", "%Y/%m/%d"]),
        (r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b",
         ["%d %B %Y", "%d %b %Y"]),
        (r"\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}\b",
         ["%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"]),
    ]

    for pattern, formats in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            for fmt in formats:
                try:
                    return datetime.strptime(match.group(0), fmt).date()
                except ValueError:
                    pass

    # Streamlit date_input needs a date; the admin should verify this fallback.
    return date.today()


def detect_category(text: str, categories: list[str]) -> str:
    lower = text.lower()

    for category, keywords in CATEGORY_RULES:
        if category in categories and any(word in lower for word in keywords):
            return category

    return "Other" if "Other" in categories else categories[0]


def detect_skills(text: str) -> str:
    """Suggest skills only when relevant terms actually appear in the text."""
    lower = text.lower()
    found = []

    for skill in SKILL_KEYWORDS:
        if skill.lower() in lower and skill not in found:
            found.append(skill)

    return ", ".join(found[:12])


def detect_description(text: str, title: str, category: str) -> str:
    """Create a short summary from certificate wording, not invented claims."""
    lines = get_lines(text)

    patterns = [
        r"[^.\n]{0,100}(?:successfully completed|completed the|"
        r"participated in|participation in|attended|qualified for|"
        r"awarded for|recognized for)[^.\n]{0,180}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            sentence = clean_line(match.group(0))
            if len(sentence) >= 20:
                return sentence[:300].rstrip(" .") + "."

    # Use extracted wording only if it is informative.
    for line in lines:
        lower = line.lower()
        if (
            25 <= len(line) <= 220
            and not any(bad in lower for bad in BAD_TITLE_PHRASES)
            and not re.search(r"\b(?:BCT/|certificate no|serial number)\b", lower)
        ):
            if re.search(
                r"\b(?:participat|complet|attend|achiev|award|training|"
                r"workshop|hackathon|quiz|course|internship|skill)\w*\b",
                lower,
            ):
                return line[:300]

    return f"Certificate categorized as {category}. Please review the original certificate and add any missing achievement details."


def analyze_certificate(
    file_bytes: bytes,
    filename: str,
    categories: list[str],
) -> dict:
    """Return suggested fields for admin review before saving."""
    text = extract_text(file_bytes, filename)

    return {
        "title": detect_title(text, filename),
        "issuer": detect_issuer(text),
        "recipient": detect_recipient(text),
        "category": detect_category(text, categories),
        "issue_date": detect_date(text),
        "credential_id": detect_credential_id(text),
        "verification_url": "",
        "skills": detect_skills(text),
        "description": detect_description(
            text,
            detect_title(text, filename),
            detect_category(text, categories),
        ),
        "extracted_text": text,
    }
