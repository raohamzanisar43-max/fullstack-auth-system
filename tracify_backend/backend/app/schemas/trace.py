"""
Trace job schemas for Tracerfy Backend
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TraceType(str, Enum):
    NORMAL = "normal"
    ENHANCED = "enhanced"


class TraceJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TraceJobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: TraceType


class TraceJobUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[TraceJobStatus] = None


class TraceJob(BaseModel):
    id: int
    user_id: int
    name: str
    type: TraceType
    status: TraceJobStatus
    total_records: int = 0
    processed_records: int = 0
    successful_records: int = 0
    credits_used: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    result_file_path: Optional[str] = None

    class Config:
        from_attributes = True


class TraceJobWithStats(TraceJob):
    progress_percentage: float = Field(default=0.0)
    success_rate: float = Field(default=0.0)
    estimated_completion: Optional[datetime] = None


class ManualSearchType(str, Enum):
    PROPERTY = "property"
    OWNER = "owner"
    PHONE = "phone"
    EMAIL = "email"


class ManualSearchCreate(BaseModel):
    search_type: ManualSearchType
    search_query: str = Field(..., min_length=1, max_length=500)


class ManualSearch(BaseModel):
    id: int
    user_id: int
    search_type: ManualSearchType
    search_query: str
    results: List[dict] = []
    credits_used: int = 0
    status: TraceJobStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyRecord(BaseModel):
    property_address: str
    property_city: str
    property_state: str
    property_zip: str
    property_county: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    owner_city: Optional[str] = None
    owner_state: Optional[str] = None
    owner_zip: Optional[str] = None
    phone_numbers: List[str] = []
    email_addresses: List[str] = []
    property_value: Optional[float] = None
    last_sale_date: Optional[datetime] = None
    last_sale_amount: Optional[float] = None
    mortgage_info: Optional[dict] = None
    lien_info: Optional[dict] = None

    class Config:
        from_attributes = True


class TraceResult(BaseModel):
    input_record: dict
    output_record: Optional[PropertyRecord] = None
    status: str
    error_message: Optional[str] = None
    credits_used: int = 1
    processing_time: Optional[float] = None

    class Config:
        from_attributes = True


class BulkTraceResults(BaseModel):
    job_id: int
    total_records: int
    successful_records: int
    failed_records: int
    results: List[TraceResult]
    summary: dict

    class Config:
        from_attributes = True
