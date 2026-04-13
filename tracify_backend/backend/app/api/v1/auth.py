"""
Authentication endpoints for Tracerfy Backend
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.db.session import get_db
from app.schemas.user import (
    User, UserLogin, UserRegister, Token, TokenRefresh,
    PasswordResetRequest, PasswordReset, EmailVerification, ResendVerification,
    UserWithTokens, UserUpdate, UserUpdatePassword
)
from app.services.user_service import UserService, APIKeyService
from app.core.exceptions import ValidationError, AuthenticationError, NotFoundError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserWithTokens, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user"""
    try:
        user_service = UserService(db)
        
        # Create user
        user = user_service.create_user(user_data)
        
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        # Create verification token
        try:
            verification_token = user_service.create_verification_token(user.id)
            # TODO: Send verification email
            # await send_verification_email(user.email, verification_token)
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to create verification token: {e}")
        
        return UserWithTokens(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            phone=user.phone,
            company=user.company,
            bio=user.bio,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            is_verified=user.is_verified,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Registration error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=UserWithTokens)
async def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate user and return tokens"""
    try:
        user_service = UserService(db)
        
        # Authenticate user
        user = user_service.authenticate_user(user_data.email, user_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return UserWithTokens(
            **user.__dict__,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except AuthenticationError as e:
        print(f"Authentication error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error during login: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {type(e).__name__}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_token(token_data.refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user exists and is active
        user_service = UserService(db)
        user = user_service.get_user_by_id(int(user_id))
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPBearer = Depends(security),
    db: Session = Depends(get_db)
) -> Any:
    """Logout user (client-side token removal)"""
    # In a stateless JWT implementation, logout is handled client-side
    # by removing the tokens. This endpoint can be used for logging or
    # for token blacklisting in a more advanced setup.
    
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(
    request_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Request password reset"""
    try:
        user_service = UserService(db)
        
        # Create reset token
        reset_token = user_service.create_password_reset_token(request_data.email)
        
        # TODO: Send password reset email
        # await send_password_reset_email(request_data.email, reset_token)
        
        return {"message": "Password reset email sent"}
        
    except NotFoundError:
        # Don't reveal if email exists or not
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
) -> Any:
    """Reset password using token"""
    try:
        user_service = UserService(db)
        
        # Reset password
        user = user_service.reset_password(reset_data.token, reset_data.new_password)
        
        return {"message": "Password reset successfully"}
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
) -> Any:
    """Verify email address"""
    try:
        user_service = UserService(db)
        
        # Verify email
        user = user_service.verify_email(verification_data.token)
        
        return {"message": "Email verified successfully"}
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )


@router.post("/resend-verification")
async def resend_verification(
    request_data: ResendVerification,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Resend email verification"""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_email(request_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Create new verification token
        verification_token = user_service.create_verification_token(user.id)
        
        # TODO: Send verification email
        # await send_verification_email(user.email, verification_token)
        
        return {"message": "Verification email sent"}
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )


@router.get("/me", response_model=User)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get current user profile"""
    # User is available from middleware
    user = getattr(request.state, 'user', None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.put("/me", response_model=User)
async def update_current_user(
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Update current user profile"""
    # User is available from middleware
    user = getattr(request.state, 'user', None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(user.id, user_data)
        return updated_user
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/change-password")
async def change_password(
    password_data: UserUpdatePassword,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Change current user password"""
    # User is available from middleware
    user = getattr(request.state, 'user', None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_service = UserService(db)
        user_service.update_user_password(user.id, password_data)
        return {"message": "Password changed successfully"}
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
