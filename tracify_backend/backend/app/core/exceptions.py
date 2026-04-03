"""
Custom Exception Classes for Tracerfy Backend
"""

from typing import Any, Dict, Optional


class BaseCustomException(Exception):
    """Base class for custom exceptions"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseCustomException):
    """Raised when input validation fails"""
    pass


class AuthenticationError(BaseCustomException):
    """Raised when authentication fails"""
    pass


class AuthorizationError(BaseCustomException):
    """Raised when authorization fails"""
    pass


class NotFoundError(BaseCustomException):
    """Raised when a resource is not found"""
    pass


class RateLimitExceeded(BaseCustomException):
    """Raised when rate limit is exceeded"""
    pass


class PaymentError(BaseCustomException):
    """Raised when payment processing fails"""
    pass


class DNCServiceError(BaseCustomException):
    """Raised when DNC (Do Not Call) service fails"""
    pass
