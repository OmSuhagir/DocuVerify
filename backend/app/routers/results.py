from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import VerificationSession
from ..schemas.schemas import SessionResult, DocumentResult, ComparisonResultModel, ExtractedData, CategoryResultModel

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/{session_id}", response_model=SessionResult)
async def get_results(session_id: str, db: Session = Depends(get_db)):
    session = db.query(VerificationSession).filter(VerificationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    documents = []
    for doc in session.documents:
        extracted = None
        if doc.extracted_data:
            extracted = ExtractedData(**doc.extracted_data)
        documents.append(DocumentResult(
            id=doc.id,
            filename=doc.filename,
            category=doc.category,
            document_type=doc.document_type,
            extracted_data=extracted
        ))

    comparisons = []
    for comp in session.comparisons:
        comparisons.append(ComparisonResultModel(
            category=comp.category,
            doc1_id=comp.doc1_id,
            doc2_id=comp.doc2_id,
            field_scores=comp.field_scores,
            average_score=comp.average_score
        ))

    category_results = []
    for cr in session.category_results:
        category_results.append(CategoryResultModel(
            category=cr.category,
            similarity_score=cr.similarity_score,
            is_valid=cr.is_valid,
            missing_fields=cr.missing_fields
        ))

    return SessionResult(
        session_id=session.id,
        documents=documents,
        comparisons=comparisons,
        category_results=category_results,
        category_scores=session.category_scores,
        overall_score=session.overall_score,
        eligible=session.eligible,
        message=session.message
    )
