"""
Credit system endpoints for Tracerfy Backend
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.credit import (
    CreditBalance, CreditPurchase, CreditPurchaseResponse, CreditUsage, CreditUsageResponse,
    CreditStats, CreditTransactionHistory, CreditPackage
)
from app.services.credit_service import CreditService
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


@router.get("/balance", response_model=CreditBalance)
async def get_credit_balance(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get user's credit balance"""
    user = get_current_user(request)
    
    try:
        credit_service = CreditService(db)
        balance = credit_service.get_user_balance(user.id)
        return balance
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit balance"
        )


@router.post("/purchase", response_model=CreditPurchaseResponse)
async def purchase_credits(
    purchase_data: CreditPurchase,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Purchase credits"""
    user = get_current_user(request)
    
    try:
        credit_service = CreditService(db)
        result = credit_service.purchase_credits(user.id, purchase_data)
        return result
        
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
            detail="Failed to purchase credits"
        )


@router.post("/use", response_model=CreditUsageResponse)
async def use_credits(
    usage_data: CreditUsage,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Use credits for services"""
    user = get_current_user(request)
    
    try:
        credit_service = CreditService(db)
        result = credit_service.use_credits(user.id, usage_data)
        return result
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to use credits"
        )


@router.get("/transactions", response_model=CreditTransactionHistory)
async def get_transaction_history(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Any:
    """Get credit transaction history"""
    user = get_current_user(request)
    
    try:
        credit_service = CreditService(db)
        history = credit_service.get_transaction_history(user.id, skip, limit)
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )


@router.get("/stats", response_model=CreditStats)
async def get_credit_stats(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get credit statistics"""
    user = get_current_user(request)
    
    try:
        credit_service = CreditService(db)
        stats = credit_service.get_credit_stats(user.id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit statistics"
        )


@router.get("/packages", response_model=List[CreditPackage])
async def get_credit_packages(
    db: Session = Depends(get_db)
) -> Any:
    """Get available credit packages"""
    try:
        credit_service = CreditService(db)
        packages = credit_service.get_available_packages()
        return packages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit packages"
        )
