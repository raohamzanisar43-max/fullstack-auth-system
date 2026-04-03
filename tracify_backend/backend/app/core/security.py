"""
Security utilities for authentication and authorization
"""

import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
import hashlib
import hmac

from app.core.config import settings


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any]
) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Truncate password to 72 bytes as required by bcrypt
    return bcrypt.checkpw(plain_password[:72].encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    # Truncate password to 72 bytes as required by bcrypt and generate salt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password[:72].encode('utf-8'), salt).decode('utf-8')


def generate_password_reset_token(email: str) -> str:
    """Generate password reset token"""
    delta = timedelta(hours=1)  # Token expires in 1 hour
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token"""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if decoded_token.get("type") != "password_reset":
            return None
        return decoded_token["sub"]
    except JWTError:
        return None


def generate_api_key() -> tuple[str, str]:
    """Generate API key and its hash"""
    # Generate random key
    key = f"tf_{secrets.token_urlsafe(32)}"
    
    # Create hash for storage
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    return key, key_hash


def verify_api_key(key: str) -> bool:
    """Verify API key format"""
    if not key.startswith("tf_"):
        return False
    
    if len(key) != 35:  # tf_ + 32 characters
        return False
    
    return True


def hash_api_key(key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(length)


def create_webhook_signature(payload: str, secret: str) -> str:
    """Create webhook signature"""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    expected_signature = create_webhook_signature(payload, secret)
    return hmac.compare_digest(signature, expected_signature)


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data for logging"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


def generate_session_token() -> str:
    """Generate session token"""
    return secrets.token_urlsafe(64)


class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_headers() -> dict:
        """Get security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }


class RateLimitTracker:
    """Simple rate limiting tracker"""
    
    def __init__(self):
        self.attempts = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed"""
        now = datetime.utcnow().timestamp()
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        # Remove old attempts
        self.attempts[key] = [
            attempt for attempt in self.attempts[key]
            if now - attempt < window
        ]
        
        # Check limit
        if len(self.attempts[key]) >= limit:
            return False
        
        # Add current attempt
        self.attempts[key].append(now)
        return True


# Global rate limit tracker
rate_limiter = RateLimitTracker()
