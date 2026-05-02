import uuid
import datetime
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from ..database import Base

class VerificationSession(Base):
    __tablename__ = "verification_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    overall_score = Column(Float, nullable=True)
    eligible = Column(Boolean, nullable=True)
    message = Column(String, nullable=True)
    category_scores = Column(JSON, nullable=True)
    
    documents = relationship("Document", back_populates="session", cascade="all, delete-orphan")
    comparisons = relationship("ComparisonResult", back_populates="session", cascade="all, delete-orphan")
    category_results = relationship("CategoryResult", back_populates="session", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("verification_sessions.id"))
    filename = Column(String)
    file_path = Column(String)
    category = Column(String, nullable=True) # IDENTIFICATION, ADDRESS, NON_ECR
    document_type = Column(String, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    raw_text = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("VerificationSession", back_populates="documents")

class CategoryResult(Base):
    __tablename__ = "category_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("verification_sessions.id"))
    category = Column(String) # IDENTIFICATION, ADDRESS, NON_ECR
    similarity_score = Column(Float, nullable=True)
    is_valid = Column(Boolean, default=False)
    missing_fields = Column(JSON, nullable=True)
    
    session = relationship("VerificationSession", back_populates="category_results")

class ComparisonResult(Base):
    __tablename__ = "comparison_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("verification_sessions.id"))
    category = Column(String, nullable=True)
    doc1_id = Column(String, ForeignKey("documents.id"))
    doc2_id = Column(String, ForeignKey("documents.id"))
    field_scores = Column(JSON)
    average_score = Column(Float)
    
    session = relationship("VerificationSession", back_populates="comparisons")
