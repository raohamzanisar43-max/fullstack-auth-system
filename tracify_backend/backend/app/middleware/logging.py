"""
Logging Middleware
Handles request/response logging, performance monitoring, and audit trails
"""

import logging
import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging
    """
    
    def __init__(self, app, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = getattr(logging, log_level.upper())
        self.start_time = None
        
        # Configure request logging
        self.request_logger = logging.getLogger("request_logger")
        self.response_logger = logging.getLogger("response_logger")
        self.performance_logger = logging.getLogger("performance_logger")
        self.audit_logger = logging.getLogger("audit_logger")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log comprehensive information
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Log request details
        await self._log_request(request, request_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response details
            await self._log_response(request, response, request_id, process_time)
            
            # Add performance headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            await self._log_error(request, e, request_id, process_time)
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Get user info if available
            user_id = getattr(request.state, "user_id", None)
            user_email = getattr(request.state, "user", {}).get("email") if hasattr(request.state, "user") else None
            
            # Get API key info if available
            api_key_name = getattr(request.state, "api_key", {}).get("name") if hasattr(request.state, "api_key") else None
            
            # Log request
            request_data = {
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
                "user_id": user_id,
                "user_email": user_email,
                "api_key_name": api_key_name,
                "timestamp": time.time()
            }
            
            self.request_logger.log(self.log_level, f"Request: {json.dumps(request_data)}")
            
            # Log sensitive operations for audit
            if self._is_sensitive_operation(request):
                await self._log_audit_event(request, request_id, "request_initiated")
                
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
    
    async def _log_response(self, request: Request, response: Response, request_id: str, process_time: float):
        """Log outgoing response details"""
        try:
            # Get user info for audit
            user_id = getattr(request.state, "user_id", None)
            
            response_data = {
                "request_id": request_id,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
                "process_time": round(process_time, 4),
                "timestamp": time.time()
            }
            
            self.response_logger.log(self.log_level, f"Response: {json.dumps(response_data)}")
            
            # Log performance metrics
            await self._log_performance(request, response, process_time)
            
            # Log sensitive operations for audit
            if self._is_sensitive_operation(request):
                await self._log_audit_event(request, request_id, "request_completed", {
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4)
                })
                
        except Exception as e:
            logger.error(f"Failed to log response: {str(e)}")
    
    async def _log_error(self, request: Request, error: Exception, request_id: str, process_time: float):
        """Log error details"""
        try:
            error_data = {
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "process_time": round(process_time, 4),
                "timestamp": time.time()
            }
            
            logger.error(f"Request error: {json.dumps(error_data)}")
            
            # Log security-related errors
            if self._is_security_error(error):
                await self._log_security_event(request, error, request_id)
                
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    async def _log_performance(self, request: Request, response: Response, process_time: float):
        """Log performance metrics"""
        try:
            performance_data = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "timestamp": time.time()
            }
            
            # Log slow requests
            if process_time > settings.SLOW_REQUEST_THRESHOLD:
                self.performance_logger.warning(
                    f"Slow request detected: {json.dumps(performance_data)}"
                )
            
            # Log all performance data for monitoring
            self.performance_logger.info(f"Performance: {json.dumps(performance_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log performance: {str(e)}")
    
    async def _log_audit_event(self, request: Request, request_id: str, event_type: str, additional_data: Optional[dict] = None):
        """Log audit events for sensitive operations"""
        try:
            user_id = getattr(request.state, "user_id", None)
            user_email = getattr(request.state, "user", {}).get("email") if hasattr(request.state, "user") else None
            client_ip = self._get_client_ip(request)
            
            audit_data = {
                "request_id": request_id,
                "event_type": event_type,
                "user_id": user_id,
                "user_email": user_email,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "timestamp": time.time()
            }
            
            if additional_data:
                audit_data.update(additional_data)
            
            self.audit_logger.info(f"Audit: {json.dumps(audit_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
    
    async def _log_security_event(self, request: Request, error: Exception, request_id: str):
        """Log security-related events"""
        try:
            client_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent")
            
            security_data = {
                "request_id": request_id,
                "event_type": "security_violation",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "timestamp": time.time()
            }
            
            logger.warning(f"Security event: {json.dumps(security_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"
    
    def _is_sensitive_operation(self, request: Request) -> bool:
        """Check if request involves sensitive operations"""
        sensitive_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/reset-password",
            "/api/v1/users",
            "/api/v1/credits/purchase",
            "/api/v1/files/upload",
            "/api/v1/admin",
            "/api/v1/api-keys"
        ]
        
        sensitive_methods = ["POST", "PUT", "DELETE", "PATCH"]
        
        return (
            request.method in sensitive_methods and
            any(request.url.path.startswith(path) for path in sensitive_paths)
        )
    
    def _is_security_error(self, error: Exception) -> bool:
        """Check if error is security-related"""
        security_errors = [
            "AuthenticationError",
            "AuthorizationError",
            "PermissionError",
            "TokenError",
            "InvalidTokenError"
        ]
        
        return type(error).__name__ in security_errors


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured JSON logging
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with structured logging"""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Structured log entry
            log_entry = {
                "event": "http_request",
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": round(process_time * 1000, 2),
                "timestamp": time.time(),
                "request_id": getattr(request.state, "request_id", None)
            }
            
            logger.info(json.dumps(log_entry))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Structured error log
            error_entry = {
                "event": "http_error",
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(process_time * 1000, 2),
                "timestamp": time.time(),
                "request_id": getattr(request.state, "request_id", None)
            }
            
            logger.error(json.dumps(error_entry))
            raise


# Middleware factory functions
def create_logging_middleware(app, log_level: str = "INFO") -> LoggingMiddleware:
    """Create logging middleware instance"""
    return LoggingMiddleware(app, log_level)


def create_structured_logging_middleware(app) -> StructuredLoggingMiddleware:
    """Create structured logging middleware instance"""
    return StructuredLoggingMiddleware(app)
