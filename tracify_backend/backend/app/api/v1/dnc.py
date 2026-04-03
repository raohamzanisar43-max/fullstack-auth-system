"""
DNC scrubbing endpoints for Tracerfy Backend
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dnc import DncScrub, DncScrubCreate, DncScrubUpdate
from app.services.dnc_service import DncService
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


@router.post("/", response_model=DncScrub, status_code=status.HTTP_201_CREATED)
async def create_dnc_scrub(
    name: str = Form(...),
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db)
) -> Any:
    """Create a new DNC scrub job"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        
        scrub_data = DncScrubCreate(name=name)
        
        dnc_scrub = dnc_service.create_dnc_scrub(user.id, scrub_data, file)
        return dnc_scrub
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create DNC scrub job"
        )


@router.get("/", response_model=List[DncScrub])
async def get_dnc_scrubs(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Any:
    """Get user's DNC scrub jobs"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        dnc_scrubs = dnc_service.get_user_dnc_scrubs(user.id, skip, limit)
        return dnc_scrubs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve DNC scrub jobs"
        )


@router.get("/{scrub_id}", response_model=DncScrub)
async def get_dnc_scrub(
    scrub_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get specific DNC scrub job"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        dnc_scrub = dnc_service.get_dnc_scrub(scrub_id, user.id)
        return dnc_scrub
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve DNC scrub job"
        )


@router.put("/{scrub_id}", response_model=DncScrub)
async def update_dnc_scrub(
    scrub_id: int,
    scrub_data: DncScrubUpdate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Update DNC scrub job"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        dnc_scrub = dnc_service.update_dnc_scrub(scrub_id, user.id, scrub_data)
        return dnc_scrub
        
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
            detail="Failed to update DNC scrub job"
        )


@router.delete("/{scrub_id}")
async def delete_dnc_scrub(
    scrub_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Delete DNC scrub job"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        dnc_service.delete_dnc_scrub(scrub_id, user.id)
        
        return {"message": "DNC scrub job deleted successfully"}
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete DNC scrub job"
        )


@router.get("/{scrub_id}/results")
async def get_dnc_scrub_results(
    scrub_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get DNC scrub job results"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        results = dnc_service.get_dnc_scrub_results(scrub_id, user.id)
        return results
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve DNC scrub job results"
        )


@router.get("/{scrub_id}/download")
async def download_dnc_results(
    scrub_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Download DNC scrub job results as CSV"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        result_file_path = dnc_service.download_dnc_results(scrub_id, user.id)
        
        return FileResponse(
            path=result_file_path,
            filename=f"dnc_results_{scrub_id}.csv",
            media_type="text/csv"
        )
        
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
            detail="Failed to download DNC results"
        )


@router.post("/check")
async def check_phone_numbers(
    phone_numbers: List[str],
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Check if phone numbers are on DNC lists"""
    user = get_current_user(request)
    
    try:
        dnc_service = DncService(db)
        results = dnc_service.check_phone_numbers(phone_numbers)
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check phone numbers"
        )


@router.get("/registry/stats")
async def get_registry_stats(
    db: Session = Depends(get_db)
) -> Any:
    """Get DNC registry statistics"""
    try:
        dnc_service = DncService(db)
        stats = dnc_service.get_registry_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve registry statistics"
        )
