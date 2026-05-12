"""
Trace job models for Tracerfy Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class TraceType(str, enum.Enum):
    NORMAL = "normal"
    ENHANCED = "enhanced"


class TraceJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ManualSearchType(str, enum.Enum):
    PROPERTY = "property"
    OWNER = "owner"
    PHONE = "phone"
    EMAIL = "email"


class TraceJob(Base):
    __tablename__ = "trace_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(TraceType), nullable=False)
    status = Column(Enum(TraceJobStatus), default=TraceJobStatus.PENDING, nullable=False)
    
    # Statistics
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    credits_used = Column(Integer, default=0)
    
    # File paths
    file_path = Column(String(500), nullable=True)
    result_file_path = Column(String(500), nullable=True)
    
    # Column mapping (JSON string)
    column_mapping = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="trace_jobs")
    results = relationship("TraceResult", back_populates="trace_job", cascade="all, delete-orphan")


class ManualSearch(Base):
    __tablename__ = "manual_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_type = Column(Enum(ManualSearchType), nullable=False)
    search_query = Column(String(500), nullable=False)
    results = Column(Text, nullable=True)  # JSON string
    credits_used = Column(Integer, default=1)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="manual_searches")


class TraceResult(Base):
    __tablename__ = "trace_results"

    id = Column(Integer, primary_key=True, index=True)
    trace_job_id = Column(Integer, ForeignKey("trace_jobs.id"), nullable=False)
    input_record = Column(Text, nullable=False)  # JSON string
    output_record = Column(Text, nullable=True)  # JSON string
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    credits_used = Column(Integer, default=1)
    processing_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trace_job = relationship("TraceJob", back_populates="results")
    property_record = relationship("PropertyRecord", back_populates="trace_result", uselist=False)


class PropertyRecord(Base):
    __tablename__ = "property_records"

    id = Column(Integer, primary_key=True, index=True)
    trace_result_id = Column(Integer, ForeignKey("trace_results.id"), nullable=True)
    
    # Property Information
    property_address = Column(String(500), nullable=False)
    property_city = Column(String(100), nullable=False)
    property_state = Column(String(2), nullable=False)
    property_zip = Column(String(10), nullable=False)
    property_county = Column(String(100), nullable=True)
    
    # Owner Information
    owner_name = Column(String(255), nullable=True)
    owner_address = Column(String(500), nullable=True)
    owner_city = Column(String(100), nullable=True)
    owner_state = Column(String(2), nullable=True)
    owner_zip = Column(String(10), nullable=True)
    
    # Contact Information
    phone_numbers = Column(Text, nullable=True)  # JSON array
    email_addresses = Column(Text, nullable=True)  # JSON array
    
    # Property Details
    property_value = Column(Float, nullable=True)
    last_sale_date = Column(DateTime, nullable=True)
    last_sale_amount = Column(Float, nullable=True)
    mortgage_info = Column(Text, nullable=True)  # JSON
    lien_info = Column(Text, nullable=True)  # JSON
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trace_result = relationship("TraceResult", back_populates="property_record")
