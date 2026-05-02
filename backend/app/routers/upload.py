from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
import shutil
import uuid
import os
from pathlib import Path
from ..schemas.schemas import UploadResponse
from ..database import get_db
from ..models.models import VerificationSession, Document
from sqlalchemy.orm import Session
from ..config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/", response_model=UploadResponse)
async def upload_documents(
    file: UploadFile = File(...),
    category: str = Form(...),
    document_type: str = Form(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not session_id:
        session_id = str(uuid.uuid4())
        session_db = VerificationSession(id=session_id)
        db.add(session_db)
    else:
        session_db = db.query(VerificationSession).filter(VerificationSession.id == session_id).first()
        if not session_db:
            session_db = VerificationSession(id=session_id)
            db.add(session_db)
            
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
        
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc = Document(
        id=file_id, 
        session_id=session_id, 
        filename=file.filename, 
        file_path=file_path,
        category=category,
        document_type=document_type
    )
    db.add(doc)
    db.commit()
    db.refresh(session_db)
    
    documents = [
        {"filename": d.filename, "category": d.category, "document_type": d.document_type}
        for d in session_db.documents
    ]
    
    return UploadResponse(session_id=session_id, documents=documents)
