"""
API Key management endpoints for Tracerfy Backend
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import APIKey, APIKeyCreate, APIKeyUpdate, APIKeyWithKey
from app.services.user_service import APIKeyService
from app.core.exceptions import ValidationError, NotFoundError

router = APIRouter()


def get_current_user(request: Request):
    """Get current user from request state"""
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/", response_model=APIKeyWithKey, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Create a new API key"""
    user = get_current_user(request)
    
    try:
        api_key_service = APIKeyService(db)
        
        # Create API key
        db_api_key, api_key = api_key_service.create_api_key(
            user.id, 
            api_key_data.dict()
        )
        
        return APIKeyWithKey(
            **db_api_key.__dict__,
            api_key=api_key
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.get("/", response_model=List[APIKey])
async def get_api_keys(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """Get user's API keys"""
    user = get_current_user(request)
    
    try:
        api_key_service = APIKeyService(db)
        api_keys = api_key_service.get_user_api_keys(user.id, skip, limit)
        return api_keys
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys"
        )


@router.get("/{api_key_id}", response_model=APIKey)
async def get_api_key(
    api_key_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get specific API key"""
    user = get_current_user(request)
    
    try:
        api_key_service = APIKeyService(db)
        api_key = api_key_service.get_api_key_by_id(api_key_id, user.id)
        return api_key
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API key"
        )


@router.put("/{api_key_id}", response_model=APIKey)
async def update_api_key(
    api_key_id: int,
    api_key_data: APIKeyUpdate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Update API key"""
    user = get_current_user(request)
    
    try:
        api_key_service = APIKeyService(db)
        
        # Update API key
        update_data = api_key_data.dict(exclude_unset=True)
        api_key = api_key_service.update_api_key(api_key_id, user.id, update_data)
        
        return api_key
        
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
            detail="Failed to update API key"
        )


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Delete API key"""
    user = get_current_user(request)
    
    try:
        api_key_service = APIKeyService(db)
        api_key_service.delete_api_key(api_key_id, user.id)
        
        return {"message": "API key deleted successfully"}
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )
