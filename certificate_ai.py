
"""Extract certificate text and suggest metadata for Certificate Vault."""

from datetime import date, datetime
import re
import io

import fitz
from PIL import Image
import pytesseract


CATEGORY_RULES = [
    ("Hackathon", ["hackathon", "innovation challenge", "hack fest"]),
    ("Quiz Competition", ["quiz competition", "tech quiz", "quiz contest"]),
    ("Coding Competition", ["coding contest", "programming contest", "code competition"]),
    ("Workshop", ["workshop", "hands-on session"]),
    ("Webinar & Seminar", ["webinar", "seminar", "guest lecture"]),
    ("Bootcamp & Training", ["bootcamp", "training program", "training programme"]),
    ("Internship", ["internship", "intern"]),
    ("Job Simulation", ["job simulation", "virtual experience program", "virtual job"]),
    ("AI & Machine Learning", ["artificial intelligence", "machine learning", "deep learning", "generative ai"]),
    ("Data Science & Analytics", ["data science", "data analytics", "data analysis"]),
    ("Programming & Software Development", ["python programming", "java programming", "software development"]),
    ("Course Completion", ["course completion", "successfully completed", "completion certificate"]),
    ("Academic Achievement", ["academic achievement", "academic excellence"]),
    ("Award & Recognition", ["winner", "first prize", "second prize", "award of excellence", "merit award"]),
    ("Volunteering & Leadership", ["volunteer", "leadership", "community service"]),
]


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Read text from a PDF or image; use OCR when PDF text is unavailable."""
    name = filename.lower()

    if name.endswith(".pdf"):
        document = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            pages = list(document)
            text = "\n".join(page.get_text("text") for page in pages[:5])

            if len(text.strip()) >= 40:
                return text[:30000]

            # Scanned PDF fallback: OCR up to the first three pages.
            ocr_text = []
            for page in pages[:3]:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text.append(pytesseract.image_to_string(image))
            return "\n".join(ocr_text)[:30000]
        finally:
            document.close()

    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return pytesseract.image_to_string(image)[:30000]


def detect_category(text: str, categories: list[str]) -> str:
    lower = text.lower()

    for category, keywords in CATEGORY_RULES:
        if category in categories and any(word in lower for word in keywords):
            return category

    return "Other" if "Other" in categories else categories[0]


def detect_date(text: str) -> date:
    """Return a likely date, or today's date if none is detected."""
    patterns = [
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
        r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
        r"\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b",
        r"\b([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})\b",
    ]

    formats = [
        ("%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"),
        ("%Y-%m-%d", "%Y/%m/%d"),
        ("%d %B %Y", "%d %b %Y"),
        ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"),
    ]

    for pattern, possible_formats in zip(patterns, formats):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(1)
            for fmt in possible_formats:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

    return date.today()


def detect_title(text: str, filename: str) -> str:
    lines = [
        re.sub(r"\s+", " ", line).strip(" :-|")
        for line in text.splitlines()
    ]
    lines = [line for line in lines if 3 <= len(line) <= 100]

    # Prefer meaningful certificate headings over arbitrary first lines.
    keywords = [
        "certificate of", "certificate", "hackathon", "participation",
        "workshop", "internship", "achievement", "completion",
        "quiz", "bootcamp", "training", "award",
    ]

    for line in lines[:35]:
        if any(word in line.lower() for word in keywords):
            return line[:100]

    clean_name = re.sub(r"\.[^.]+$", "", filename)
    clean_name = re.sub(r"[_-]+", " ", clean_name).strip()
    return clean_name[:100] or "Untitled Certificate"


def detect_recipient(text: str) -> str:
    patterns = [
        r"(?:this is to certify that|awarded to|presented to|certify that)\s*[:\-]?\s*([A-Z][A-Za-z.' -]{2,70})",
        r"(?:participant name|student name|recipient)\s*[:\-]\s*([A-Z][A-Za-z.' -]{2,70})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" .,-")[:70]

    return ""


def detect_issuer(text: str) -> str:
    lines = [
        re.sub(r"\s+", " ", line).strip(" :-|")
        for line in text.splitlines()
    ]
    lines = [line for line in lines if 3 <= len(line) <= 100]

    # Heuristic only: an issuer needs confirmation by the admin.
    skip = ("certificate", "congratulations", "this is to certify",
            "awarded to", "presented to", "date:", "credential id")

    for line in lines[:12]:
        if not any(term in line.lower() for term in skip):
            return line[:100]

    return ""


def analyze_certificate(
    file_bytes: bytes,
    filename: str,
    categories: list[str],
) -> dict:
    """Return suggested metadata; never treat extraction as verification."""
    text = extract_text(file_bytes, filename)

    credential_match = re.search(
        r"(?:credential\s*id|certificate\s*id|certificate\s*number|certification\s*id)"
        r"\s*[:#\-]?\s*([A-Z0-9][A-Z0-9/_\-]{3,})",
        text,
        flags=re.IGNORECASE,
    )

    return {
        "title": detect_title(text, filename),
        "issuer": detect_issuer(text),
        "recipient": detect_recipient(text),
        "category": detect_category(text, categories),
        "issue_date": detect_date(text),
        "credential_id": credential_match.group(1) if credential_match else "",
        "verification_url": "",
        "skills": "",
        "description": "",
        "extracted_text": text,
    }
