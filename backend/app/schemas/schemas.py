from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Any

class UploadResponse(BaseModel):
    session_id: str
    documents: List[dict] # e.g. [{"filename": "...", "category": "...", "document_type": "..."}]

class ExtractedData(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    degree_title: Optional[str] = None
    candidate_name: Optional[str] = None
    date_year: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentResult(BaseModel):
    id: str
    filename: str
    category: Optional[str] = None
    document_type: Optional[str] = None
    extracted_data: Optional[ExtractedData] = None

    model_config = ConfigDict(from_attributes=True)

class CategoryResultModel(BaseModel):
    category: str
    similarity_score: Optional[float] = None
    is_valid: bool
    missing_fields: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class ComparisonResultModel(BaseModel):
    category: Optional[str] = None
    doc1_id: str
    doc2_id: str
    field_scores: Dict[str, float]
    average_score: float

    model_config = ConfigDict(from_attributes=True)

class VerifyResponse(BaseModel):
    session_id: str
    overall_score: float
    eligible: bool
    message: str
    category_scores: Optional[Dict[str, float]] = None

class SessionResult(BaseModel):
    session_id: str
    documents: List[DocumentResult]
    comparisons: List[ComparisonResultModel]
    category_results: List[CategoryResultModel]
    category_scores: Optional[Dict[str, float]] = None
    overall_score: Optional[float] = None
    eligible: Optional[bool] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
