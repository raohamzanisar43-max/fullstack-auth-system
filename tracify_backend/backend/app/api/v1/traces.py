"""
Trace job endpoints for Tracerfy Backend
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trace import TraceJob, TraceJobCreate, TraceJobUpdate, ManualSearch, ManualSearchCreate
from app.services.trace_service import TraceService
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


@router.post("/", response_model=TraceJob, status_code=status.HTTP_201_CREATED)
async def create_trace_job(
    name: str = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db)
) -> Any:
    """Create a new trace job"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        
        job_data = TraceJobCreate(
            name=name,
            type=type
        )
        
        trace_job = trace_service.create_trace_job(user.id, job_data, file)
        return trace_job
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trace job"
        )


@router.get("/", response_model=List[TraceJob])
async def get_trace_jobs(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Any:
    """Get user's trace jobs"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        trace_jobs = trace_service.get_user_trace_jobs(user.id, skip, limit)
        return trace_jobs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trace jobs"
        )


@router.get("/{job_id}", response_model=TraceJob)
async def get_trace_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get specific trace job"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        trace_job = trace_service.get_trace_job(job_id, user.id)
        return trace_job
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trace job"
        )


@router.put("/{job_id}", response_model=TraceJob)
async def update_trace_job(
    job_id: int,
    job_data: TraceJobUpdate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Update trace job"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        trace_job = trace_service.update_trace_job(job_id, user.id, job_data)
        return trace_job
        
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
            detail="Failed to update trace job"
        )


@router.delete("/{job_id}")
async def delete_trace_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Delete trace job"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        trace_service.delete_trace_job(job_id, user.id)
        
        return {"message": "Trace job deleted successfully"}
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete trace job"
        )


@router.get("/{job_id}/results")
async def get_trace_job_results(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get trace job results"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        results = trace_service.get_trace_job_results(job_id, user.id)
        return results
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trace job results"
        )


@router.get("/{job_id}/download")
async def download_trace_results(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Download trace job results as CSV"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        result_file_path = trace_service.download_trace_results(job_id, user.id)
        
        return FileResponse(
            path=result_file_path,
            filename=f"trace_results_{job_id}.csv",
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
            detail="Failed to download trace results"
        )


# Manual Search endpoints
@router.post("/manual-search", response_model=ManualSearch, status_code=status.HTTP_201_CREATED)
async def create_manual_search(
    search_data: ManualSearchCreate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Create a manual search"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        manual_search = trace_service.create_manual_search(user.id, search_data)
        return manual_search
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create manual search"
        )


@router.get("/manual-search", response_model=List[ManualSearch])
async def get_manual_searches(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Any:
    """Get user's manual searches"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        searches = trace_service.get_user_manual_searches(user.id, skip, limit)
        return searches
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve manual searches"
        )


@router.get("/manual-search/{search_id}", response_model=ManualSearch)
async def get_manual_search(
    search_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get specific manual search"""
    user = get_current_user(request)
    
    try:
        trace_service = TraceService(db)
        search = trace_service.get_manual_search(search_id, user.id)
        return search
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve manual search"
        )
