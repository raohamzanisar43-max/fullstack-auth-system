"""
DNC scrubbing models for Tracerfy Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class DncScrubStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DncScrubJob(Base):
    __tablename__ = "dnc_scrub_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(DncScrubStatus), default=DncScrubStatus.PENDING, nullable=False)
    
    # Statistics
    total_records = Column(Integer, default=0)
    clean_records = Column(Integer, default=0)
    dnc_records = Column(Integer, default=0)
    credits_used = Column(Integer, default=0)
    
    # File paths
    file_path = Column(Text, nullable=True)
    result_file_path = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="dnc_scrub_jobs")
    results = relationship("DncScrubResult", back_populates="scrub_job", cascade="all, delete-orphan")


class DncScrubResult(Base):
    __tablename__ = "dnc_scrub_results"

    id = Column(Integer, primary_key=True, index=True)
    scrub_job_id = Column(Integer, ForeignKey("dnc_scrub_jobs.id"), nullable=False)
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
    scrub_job = relationship("DncScrubJob", back_populates="results")


class DncRecord(Base):
    __tablename__ = "dnc_records"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    is_dnc = Column(Boolean, default=False, nullable=False)
    dnc_type = Column(String(50), nullable=True)  # federal, state, dma, tcpa_litigator
    dnc_source = Column(String(255), nullable=True)
    first_seen_date = Column(DateTime, nullable=True)
    last_seen_date = Column(DateTime, nullable=True)
    additional_info = Column(Text, nullable=True)  # JSON
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DncRegistryStats(Base):
    __tablename__ = "dnc_registry_stats"

    id = Column(Integer, primary_key=True, index=True)
    federal_dnc_count = Column(Integer, default=0)
    state_dnc_count = Column(Integer, default=0)
    dma_count = Column(Integer, default=0)
    tcpa_litigator_count = Column(Integer, default=0)
    total_records = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
