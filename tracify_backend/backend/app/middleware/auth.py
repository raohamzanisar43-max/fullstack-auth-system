"""
Authentication Middleware
Handles JWT token validation and user authentication
"""

import logging
from typing import Optional, Callable
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.security import verify_token
from app.models.user import User
from app.db.session import get_db

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT authentication for protected routes
    """
    
    def __init__(self, app, public_paths: Optional[list] = None):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password"
        ]
        self.security = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate JWT token for protected routes
        """
        # Skip authentication for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Extract and validate token
            credentials: Optional[HTTPAuthorizationCredentials] = await self.security(request)
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify JWT token
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Get user from database
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User account is inactive",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Add user to request state
                request.state.user = user
                request.state.user_id = user.id
                
            finally:
                db.close()
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return await call_next(request)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle API key authentication for API endpoints
    """
    
    def __init__(self, app, api_key_header: str = "X-API-Key"):
        super().__init__(app)
        self.api_key_header = api_key_header
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate API key for API routes
        """
        # Only apply to API routes
        if "/api/" not in request.url.path:
            return await call_next(request)
        
        # Check for API key in header
        api_key = request.headers.get(self.api_key_header)
        
        if api_key:
            # Validate API key
            db = next(get_db())
            try:
                from app.models.api_key import APIKey
                from app.core.security import verify_api_key
                
                # Get API key from database
                key_obj = db.query(APIKey).filter(APIKey.key == api_key).first()
                
                if key_obj and key_obj.is_active and verify_api_key(api_key):
                    # Add API key info to request state
                    request.state.api_key = key_obj
                    request.state.user_id = key_obj.user_id
                    request.state.is_api_request = True
                    
                    # Log API usage
                    logger.info(f"API key {key_obj.name} used for {request.method} {request.url.path}")
                else:
                    logger.warning(f"Invalid API key used for {request.url.path}")
                    
            finally:
                db.close()
        
        return await call_next(request)


class RoleBasedAccessMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle role-based access control
    """
    
    def __init__(self, app, role_requirements: Optional[dict] = None):
        super().__init__(app)
        self.role_requirements = role_requirements or {
            "/api/v1/admin": ["admin"],
            "/api/v1/users": ["admin", "manager"],
            "/api/v1/analytics": ["admin", "manager", "analyst"]
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check user roles for protected routes
        """
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        
        if not user:
            # If no user, let auth middleware handle it
            return await call_next(request)
        
        # Check if this path requires specific roles
        for path_pattern, required_roles in self.role_requirements.items():
            if request.url.path.startswith(path_pattern):
                if user.role not in required_roles:
                    logger.warning(
                        f"User {user.email} (role: {user.role}) "
                        f"attempted to access {request.url.path} "
                        f"requiring roles: {required_roles}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
                break
        
        return await call_next(request)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle multi-tenancy if needed
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add tenant context to request
        """
        # Get user from request state
        user = getattr(request.state, "user", None)
        
        if user:
            # Add tenant information to request state
            request.state.tenant_id = user.tenant_id if hasattr(user, 'tenant_id') else None
            request.state.user_role = user.role
        
        return await call_next(request)


# Middleware factory function
def create_auth_middleware(app, public_paths: Optional[list] = None) -> AuthenticationMiddleware:
    """Create authentication middleware instance"""
    return AuthenticationMiddleware(app, public_paths)


def create_api_key_middleware(app, api_key_header: str = "X-API-Key") -> APIKeyMiddleware:
    """Create API key middleware instance"""
    return APIKeyMiddleware(app, api_key_header)


def create_role_middleware(app, role_requirements: Optional[dict] = None) -> RoleBasedAccessMiddleware:
    """Create role-based access middleware instance"""
    return RoleBasedAccessMiddleware(app, role_requirements)


def create_tenant_middleware(app) -> TenantMiddleware:
    """Create tenant middleware instance"""
    return TenantMiddleware(app)
