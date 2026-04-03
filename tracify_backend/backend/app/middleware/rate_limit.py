"""
Rate Limiting Middleware
Handles API rate limiting and throttling to prevent abuse
"""

import time
import asyncio
import logging
from typing import Dict, Optional, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis
from collections import defaultdict, deque

from app.core.config import settings
from app.core.exceptions import RateLimitExceeded

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    """
    
    def __init__(
        self,
        app,
        redis_url: Optional[str] = None,
        default_limits: Optional[Dict[str, Tuple[int, int]]] = None
    ):
        super().__init__(app)
        self.redis_client = None
        self.default_limits = default_limits or {
            "default": (100, 60),      # 100 requests per minute
            "auth": (10, 60),          # 10 auth requests per minute
            "upload": (5, 60),         # 5 uploads per minute
            "trace": (20, 60),         # 20 trace requests per minute
            "api": (1000, 60),         # 1000 API requests per minute for API keys
            "admin": (200, 60),        # 200 admin requests per minute
        }
        
        # Initialize Redis if available
        if redis_url or settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(redis_url or settings.REDIS_URL, decode_responses=True)
                self.redis_client.ping()  # Test connection
                logger.info("Rate limiting middleware initialized with Redis")
            except Exception as e:
                logger.warning(f"Redis not available for rate limiting: {str(e)}")
                self.redis_client = None
        
        # Fallback to in-memory storage
        if not self.redis_client:
            self.memory_store = defaultdict(lambda: deque())
            logger.info("Rate limiting middleware using in-memory storage")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with rate limiting
        """
        try:
            # Get client identifier
            client_id = self._get_client_id(request)
            
            # Get rate limit for this endpoint
            limit, window = self._get_rate_limit(request)
            
            # Check rate limit
            remaining, reset_time = await self._check_rate_limit(
                client_id, limit, window
            )
            
            # Process request if not rate limited
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            
            return response
            
        except RateLimitExceeded as e:
            # Return rate limit exceeded response
            return Response(
                content='{"error": "Rate limit exceeded", "message": "' + str(e) + '"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(e.retry_after),
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(e.reset_time)
                },
                media_type="application/json"
            )
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {str(e)}")
            # Allow request to proceed if rate limiting fails
            return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier for rate limiting
        Priority: API Key > User ID > IP Address
        """
        # Check for API key
        api_key = getattr(request.state, "api_key", None)
        if api_key:
            return f"api_key:{api_key.key}"
        
        # Check for authenticated user
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
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
    
    def _get_rate_limit(self, request: Request) -> Tuple[int, int]:
        """
        Get rate limit (requests, window_seconds) for this endpoint
        """
        path = request.url.path
        
        # Check for specific path limits
        if any(path.startswith(prefix) for prefix in ["/api/v1/auth", "/auth"]):
            return self.default_limits["auth"]
        elif path.startswith("/api/v1/upload") or path.startswith("/upload"):
            return self.default_limits["upload"]
        elif path.startswith("/api/v1/trace") or path.startswith("/trace"):
            return self.default_limits["trace"]
        elif path.startswith("/api/v1/admin") or path.startswith("/admin"):
            return self.default_limits["admin"]
        elif getattr(request.state, "is_api_request", False):
            return self.default_limits["api"]
        else:
            return self.default_limits["default"]
    
    async def _check_rate_limit(self, client_id: str, limit: int, window: int) -> Tuple[int, int]:
        """
        Check if client has exceeded rate limit
        Returns: (remaining_requests, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - window
        
        if self.redis_client:
            return await self._check_redis_rate_limit(client_id, limit, window, current_time)
        else:
            return self._check_memory_rate_limit(client_id, limit, window, current_time)
    
    async def _check_redis_rate_limit(
        self, client_id: str, limit: int, window: int, current_time: int
    ) -> Tuple[int, int]:
        """Check rate limit using Redis sliding window"""
        try:
            key = f"rate_limit:{client_id}"
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, current_time - window)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window)
            
            results = pipe.execute()
            
            current_requests = results[1]
            
            if current_requests >= limit:
                # Rate limit exceeded
                reset_time = current_time + window
                retry_after = window
                
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {limit} requests per {window} seconds",
                    limit=limit,
                    reset_time=reset_time,
                    retry_after=retry_after
                )
            
            remaining = limit - current_requests - 1  # -1 for current request
            reset_time = current_time + window
            
            return remaining, reset_time
            
        except redis.RedisError as e:
            logger.error(f"Redis rate limiting error: {str(e)}")
            # Fall back to memory-based rate limiting
            return self._check_memory_rate_limit(client_id, limit, window, current_time)
    
    def _check_memory_rate_limit(
        self, client_id: str, limit: int, window: int, current_time: int
    ) -> Tuple[int, int]:
        """Check rate limit using in-memory sliding window"""
        window_start = current_time - window
        client_requests = self.memory_store[client_id]
        
        # Remove expired requests
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        # Check if limit exceeded
        if len(client_requests) >= limit:
            reset_time = max(client_requests) + window
            retry_after = reset_time - current_time
            
            raise RateLimitExceeded(
                f"Rate limit exceeded: {limit} requests per {window} seconds",
                limit=limit,
                reset_time=reset_time,
                retry_after=retry_after
            )
        
        # Add current request
        client_requests.append(current_time)
        
        # Clean up old entries periodically
        if len(self.memory_store) > 10000:  # Prevent memory bloat
            self._cleanup_memory_store(current_time)
        
        remaining = limit - len(client_requests)
        reset_time = current_time + window
        
        return remaining, reset_time
    
    def _cleanup_memory_store(self, current_time: int):
        """Clean up expired entries from memory store"""
        expired_keys = []
        
        for client_id, requests in self.memory_store.items():
            # Remove expired requests
            window_start = current_time - 300  # 5 minutes
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Mark empty clients for removal
            if not requests:
                expired_keys.append(client_id)
        
        # Remove empty clients
        for key in expired_keys:
            del self.memory_store[key]


class AdvancedRateLimitMiddleware(RateLimitMiddleware):
    """
    Advanced rate limiting with multiple strategies
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.burst_limits = {
            "default": (20, 10),   # 20 requests in 10 seconds
            "auth": (5, 10),       # 5 auth requests in 10 seconds
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with advanced rate limiting (burst + sustained)
        """
        try:
            client_id = self._get_client_id(request)
            
            # Check burst limit first
            burst_limit, burst_window = self._get_burst_limit(request)
            await self._check_rate_limit(client_id, burst_limit, burst_window)
            
            # Check sustained limit
            sustained_limit, sustained_window = self._get_rate_limit(request)
            remaining, reset_time = await self._check_rate_limit(
                client_id, sustained_limit, sustained_window
            )
            
            # Process request
            response = await call_next(request)
            
            # Add headers for sustained limit
            response.headers["X-RateLimit-Limit"] = str(sustained_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            
            return response
            
        except RateLimitExceeded:
            raise
        except Exception as e:
            logger.error(f"Advanced rate limiting error: {str(e)}")
            return await call_next(request)
    
    def _get_burst_limit(self, request: Request) -> Tuple[int, int]:
        """Get burst rate limit for this endpoint"""
        path = request.url.path
        
        if any(path.startswith(prefix) for prefix in ["/api/v1/auth", "/auth"]):
            return self.burst_limits["auth"]
        else:
            return self.burst_limits["default"]


class IPRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple IP-based rate limiting for basic protection
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.ip_requests = defaultdict(lambda: deque())
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Simple IP-based rate limiting"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old requests
        requests = self.ip_requests[client_ip]
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check limit
        if len(requests) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests from this IP"
            )
        
        # Add current request
        requests.append(current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


# Middleware factory functions
def create_rate_limit_middleware(
    app,
    redis_url: Optional[str] = None,
    default_limits: Optional[Dict[str, Tuple[int, int]]] = None
) -> RateLimitMiddleware:
    """Create rate limiting middleware instance"""
    return RateLimitMiddleware(app, redis_url, default_limits)


def create_advanced_rate_limit_middleware(app, **kwargs) -> AdvancedRateLimitMiddleware:
    """Create advanced rate limiting middleware instance"""
    return AdvancedRateLimitMiddleware(app, **kwargs)


def create_ip_rate_limit_middleware(app, requests_per_minute: int = 60) -> IPRateLimitMiddleware:
    """Create IP-based rate limiting middleware instance"""
    return IPRateLimitMiddleware(app, requests_per_minute)
