"""
DNC scrubbing schemas for Tracerfy Backend
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DncScrubStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DncScrubCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class DncScrubUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[DncScrubStatus] = None


class DncScrub(BaseModel):
    id: int
    user_id: int
    name: str
    total_records: int = 0
    clean_records: int = 0
    dnc_records: int = 0
    status: DncScrubStatus
    credits_used: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    result_file_path: Optional[str] = None

    class Config:
        from_attributes = True


class DncScrubWithStats(DncScrub):
    progress_percentage: float = Field(default=0.0)
    dnc_rate: float = Field(default=0.0)
    estimated_completion: Optional[datetime] = None


class DncRecord(BaseModel):
    input_phone: str
    is_dnc: bool
    dnc_type: Optional[str] = None  # federal, state, dma, etc.
    dnc_source: Optional[str] = None
    first_seen_date: Optional[datetime] = None
    last_seen_date: Optional[datetime] = None
    additional_info: Optional[dict] = None

    class Config:
        from_attributes = True


class DncResult(BaseModel):
    input_record: dict
    output_record: Optional[DncRecord] = None
    status: str
    error_message: Optional[str] = None
    credits_used: int = 1
    processing_time: Optional[float] = None

    class Config:
        from_attributes = True


class BulkDncResults(BaseModel):
    scrub_id: int
    total_records: int
    clean_records: int
    dnc_records: int
    results: List[DncResult]
    summary: dict

    class Config:
        from_attributes = True


class DncRegistryStats(BaseModel):
    federal_dnc_count: int
    state_dnc_count: int
    dma_count: int
    tcpa_litigator_count: int
    total_records: int
    last_updated: datetime

    class Config:
        from_attributes = True
