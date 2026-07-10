"""
SQLAlchemy ORM Models for Contract & Legal Document Risk Analyzer
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default='user', nullable=False)  # 'admin' or 'user'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    documents = relationship('Document', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, image, etc.
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    extracted_text = Column(Text, nullable=True)  # OCR/parsed text content
    
    # Relationships
    user = relationship('User', back_populates='documents')
    analyses = relationship('Analysis', back_populates='document', cascade='all, delete-orphan')
    risk_reports = relationship('RiskReport', back_populates='document', cascade='all, delete-orphan')
    summaries = relationship('Summary', back_populates='document', cascade='all, delete-orphan')
    reports = relationship('Report', back_populates='document', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', user_id={self.user_id})>"


class Analysis(Base):
    """Analysis model for extracted contract details"""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    
    # Contract-specific fields
    contract_type = Column(String(255), nullable=True)
    parties = Column(Text, nullable=True)  # JSON array of parties
    effective_date = Column(String(100), nullable=True)
    expiry_date = Column(String(100), nullable=True)
    payment_terms = Column(Text, nullable=True)
    renewal_clause = Column(Text, nullable=True)
    termination_clause = Column(Text, nullable=True)
    confidentiality = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    jurisdiction = Column(String(255), nullable=True)
    
    # Full structured data as JSON
    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship('Document', back_populates='analyses')
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, document_id={self.document_id}, contract_type='{self.contract_type}')>"


class RiskReport(Base):
    """Risk report model for identified risks in documents"""
    __tablename__ = 'risk_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    
    # Risk details
    risk_title = Column(String(255), nullable=False)
    risk_level = Column(String(50), nullable=False)  # high, medium, low
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    explanation = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship('Document', back_populates='risk_reports')
    
    def __repr__(self):
        return f"<RiskReport(id={self.id}, document_id={self.document_id}, risk_level='{self.risk_level}')>"


class Summary(Base):
    """Executive summary model for contract overview"""
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    
    # Summary fields
    executive_summary = Column(Text, nullable=True)
    key_obligations = Column(Text, nullable=True)  # JSON array
    important_dates = Column(Text, nullable=True)  # JSON array
    important_clauses = Column(Text, nullable=True)  # JSON array
    payment_summary = Column(Text, nullable=True)
    termination_summary = Column(Text, nullable=True)
    risk_summary = Column(Text, nullable=True)
    recommended_actions = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship('Document', back_populates='summaries')
    
    def __repr__(self):
        return f"<Summary(id={self.id}, document_id={self.document_id})>"


class Report(Base):
    """Generated report model (PDF/DOCX exports)"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    
    report_type = Column(String(20), nullable=False)  # 'pdf' or 'docx'
    file_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship('Document', back_populates='reports')
    
    def __repr__(self):
        return f"<Report(id={self.id}, document_id={self.document_id}, report_type='{self.report_type}')>"
        