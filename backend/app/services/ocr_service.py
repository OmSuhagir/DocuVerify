import os
import pytesseract
from PIL import Image
import pdfplumber
import re
from pathlib import Path
from typing import Dict, Any

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Common name prefixes/titles to strip
TITLES = re.compile(r'\b(MR|MRS|MS|DR|MISS|SRI|SMT|KUM)\b\.?', re.IGNORECASE)

# Date patterns - covers DD/MM/YYYY, MM-DD-YYYY, YYYY-MM-DD, "25 April 2000", etc.
DATE_PATTERNS = [
    re.compile(r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b'),
    re.compile(r'\b(\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})\b'),
    re.compile(r'\b(\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\b', re.IGNORECASE),
    re.compile(r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b', re.IGNORECASE),
]

# DOB indicator lines
DOB_INDICATORS = re.compile(
    r'(?:date\s+of\s+birth|dob|d\.o\.b|born|birth\s+date)[:\s]*(.+)',
    re.IGNORECASE
)

# Name indicator lines
NAME_INDICATORS = re.compile(
    r'(?:name|full\s+name|applicant\s+name|holder)[:\s]+([A-Z][a-zA-Z\s]{2,40})',
    re.IGNORECASE
)

# Address indicator lines
ADDRESS_INDICATORS = re.compile(
    r'(?:address|addr|residence|residing\s+at|permanent\s+address)[:\s]*(.+(?:\n.+){0,3})',
    re.IGNORECASE
)

# City/place indicators
CITY_INDICATORS = re.compile(
    r'(?:city|town|place|district)[:\s]+([A-Za-z\s]{2,30})',
    re.IGNORECASE
)

# Pin/Zip code to help identify address lines
PINCODE = re.compile(r'\b\d{5,6}\b')


def extract_text_from_file(file_path: str) -> str:
    file_path = os.path.abspath(file_path)
    ext = Path(file_path).suffix.lower()
    text = ""
    if ext == ".pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")
    else:
        try:
            img = Image.open(file_path)
            # Try multiple PSM modes for best coverage
            for psm in [3, 6, 11]:
                try:
                    t = pytesseract.image_to_string(img, config=f'--psm {psm}')
                    if len(t.strip()) > len(text.strip()):
                        text = t
                except Exception:
                    pass
        except Exception as e:
            print(f"Tesseract OCR failed: {e}")
    return text


def _find_date(text: str) -> str:
    # First: look near DOB keywords
    m = DOB_INDICATORS.search(text)
    if m:
        snippet = m.group(1)[:40]
        for pat in DATE_PATTERNS:
            dm = pat.search(snippet)
            if dm:
                return dm.group(1)

    # Fallback: find any date in document
    for pat in DATE_PATTERNS:
        dm = pat.search(text)
        if dm:
            return dm.group(1)
    return ""


def _find_name(text: str, nlp_doc) -> str:
    # First: look near Name keywords
    m = NAME_INDICATORS.search(text)
    if m:
        candidate = m.group(1).strip()
        # Filter out lines that are clearly not names
        if 2 < len(candidate) < 60 and not re.search(r'\d', candidate):
            return TITLES.sub('', candidate).strip()

    # Fallback: spaCy PERSON entity
    if nlp_doc:
        for ent in nlp_doc.ents:
            if ent.label_ == "PERSON" and len(ent.text) > 3:
                return TITLES.sub('', ent.text).strip()
    return ""


def _find_address(text: str) -> str:
    m = ADDRESS_INDICATORS.search(text)
    if m:
        raw = m.group(0)
        # Take up to 3 continuation lines
        lines = [l.strip() for l in raw.splitlines() if l.strip()][:4]
        return " ".join(lines)

    # Fallback: find the line containing a pincode
    for line in text.splitlines():
        if PINCODE.search(line) and len(line.strip()) > 10:
            return line.strip()
    return ""


def _find_city(text: str, nlp_doc) -> str:
    m = CITY_INDICATORS.search(text)
    if m:
        return m.group(1).strip()

    # spaCy GPE entities
    if nlp_doc:
        for ent in nlp_doc.ents:
            if ent.label_ == "GPE" and len(ent.text) > 2:
                return ent.text.strip()
    return ""


def parse_extracted_text(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {"name": None, "dob": None, "address": None, "city": None}

    if not text or len(text.strip()) < 10:
        return data

    nlp_doc = nlp(text[:5000]) if nlp else None

    name = _find_name(text, nlp_doc)
    if name:
        data["name"] = name

    dob = _find_date(text)
    if dob:
        data["dob"] = dob

    address = _find_address(text)
    if address:
        data["address"] = address

    city = _find_city(text, nlp_doc)
    if city:
        data["city"] = city

    return data


def extract_with_ocr(file_path: str) -> Dict[str, Any]:
    text = extract_text_from_file(file_path)
    print(f"[OCR] Extracted text ({len(text)} chars) from {file_path}")
    print(f"[OCR] First 500 chars: {text[:500]}")
    result = parse_extracted_text(text)
    print(f"[OCR] Parsed result: {result}")
    return result
