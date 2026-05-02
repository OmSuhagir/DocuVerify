from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import VerificationSession, Document, ComparisonResult, CategoryResult
from ..schemas.schemas import VerifyResponse
from ..services.extraction_service import extract_document_data
from ..services.category_service import verify_session_documents, determine_final_eligibility

router = APIRouter(prefix="/verify", tags=["Verify"])

@router.post("/{session_id}", response_model=VerifyResponse)
async def verify_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(VerificationSession).filter(VerificationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.documents:
        raise HTTPException(status_code=400, detail="No documents in session")

    # Group docs by category
    id_docs = [d for d in session.documents if d.category == "IDENTIFICATION"]
    addr_docs = [d for d in session.documents if d.category == "ADDRESS"]
    non_ecr_docs = [d for d in session.documents if d.category == "NON_ECR"]

    if len(id_docs) < 3: # Assuming adult case minimum 3
        raise HTTPException(status_code=400, detail=f"Minimum 3 IDENTIFICATION documents required. Found {len(id_docs)}")
    if len(addr_docs) < 1:
        raise HTTPException(status_code=400, detail=f"Minimum 1 ADDRESS document required. Found {len(addr_docs)}")
    if len(non_ecr_docs) < 1:
        raise HTTPException(status_code=400, detail=f"Minimum 1 NON_ECR document required. Found {len(non_ecr_docs)}")

    # Idempotency guard
    if session.overall_score is not None:
        return VerifyResponse(
            session_id=session_id,
            overall_score=session.overall_score,
            eligible=session.eligible,
            message=session.message,
            category_scores=session.category_scores
        )

    # Extraction
    for doc in session.documents:
        if not doc.extracted_data:
            extracted = extract_document_data(doc.file_path, doc.category)
            doc.extracted_data = extracted
            db.add(doc)
    db.commit()

    # Global Verification
    overall_score, comparisons, category_scores = verify_session_documents(session.documents)

    # Save Comparisons
    for comp in comparisons:
        db.add(ComparisonResult(session_id=session_id, **comp))

    # Save Category Results
    id_result = CategoryResult(
        session_id=session_id, 
        category="IDENTIFICATION", 
        similarity_score=category_scores["IDENTIFICATION"], 
        is_valid=(category_scores["IDENTIFICATION"] >= 0.90)
    )
    addr_result = CategoryResult(
        session_id=session_id, 
        category="ADDRESS", 
        similarity_score=category_scores["ADDRESS"], 
        is_valid=(category_scores["ADDRESS"] >= 0.80)
    )
    non_ecr_result = CategoryResult(
        session_id=session_id, 
        category="NON_ECR", 
        similarity_score=category_scores["NON_ECR"], 
        is_valid=(category_scores["NON_ECR"] >= 0.95)
    )
    
    db.add_all([id_result, addr_result, non_ecr_result])

    # Final Eligibility
    eligible, message = determine_final_eligibility(overall_score, category_scores)

    session.overall_score = overall_score
    session.eligible = eligible
    session.message = message
    session.category_scores = category_scores
    db.add(session)
    db.commit()

    return VerifyResponse(
        session_id=session_id,
        overall_score=overall_score,
        eligible=eligible,
        message=message,
        category_scores=category_scores
    )
