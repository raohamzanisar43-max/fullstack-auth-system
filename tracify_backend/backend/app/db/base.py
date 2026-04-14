from app.db.session import Base

# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.api_key import APIKey
from app.models.credit import CreditBalance, CreditTransaction, CreditPackage
from app.models.trace import TraceJob, ManualSearch, TraceResult, PropertyRecord
from app.models.dnc import DncScrubJob, DncScrubResult, DncRecord

# Make sure all models are imported here so they get registered
__all__ = [
    "Base", 
    "User", 
    "APIKey", 
    "CreditBalance", 
    "CreditTransaction", 
    "CreditPackage",
    "TraceJob",
    "ManualSearch",
    "TraceResult",
    "PropertyRecord",
    "DncScrubJob",
    "DncScrubResult",
    "DncRecord"
]
