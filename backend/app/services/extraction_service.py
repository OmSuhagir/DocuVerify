from typing import Dict, Any
from ..config import settings
from .gemini_service import extract_with_gemini
from .ocr_service import extract_with_ocr
from ..utils.normalization import normalize_name, normalize_dob, normalize_address, normalize_city

def extract_document_data(file_path: str, category: str = None) -> Dict[str, Any]:
    raw_data = None
    
    if settings.EXTRACTION_BACKEND == "gemini" and settings.GEMINI_API_KEY:
        try:
            raw_data = extract_with_gemini(file_path, category)
        except Exception as e:
            print(f"Gemini extraction failed, falling back to OCR: {e}")
            raw_data = extract_with_ocr(file_path) # We could pass category here too, but for now fallback is OCR
    else:
        raw_data = extract_with_ocr(file_path)
        
    normalized_data = {
        "name": normalize_name(raw_data.get("name", "")),
        "dob": normalize_dob(raw_data.get("dob", "")),
        "address": normalize_address(raw_data.get("address", "")),
        "city": normalize_city(raw_data.get("city", "")),
        "degree_title": raw_data.get("degree_title", ""),
        "candidate_name": normalize_name(raw_data.get("candidate_name", "")),
        "date_year": raw_data.get("date_year", "")
    }
    
    # Clean up empty keys
    normalized_data = {k: v for k, v in normalized_data.items() if v}
    
    return normalized_data
