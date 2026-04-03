"""
Dashboard endpoints for Tracerfy Backend
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.trace import TraceJob, ManualSearch, TraceJobStatus, TraceType
from app.models.credit import CreditTransaction, CreditTransactionType
from app.services.credit_service import CreditService
from app.services.trace_service import TraceService

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


@router.get("/stats")
async def get_dashboard_stats(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Get dashboard statistics"""
    user = get_current_user(request)
    
    try:
        # Get trace job statistics
        trace_stats = (
            db.query(
                func.count(TraceJob.id).label('total_jobs'),
                func.sum(TraceJob.total_records).label('total_properties'),
                func.sum(TraceJob.successful_records).label('successful_traces'),
                func.sum(TraceJob.credits_used).label('total_credits_used')
            )
            .filter(TraceJob.user_id == user.id)
            .first()
        )
        
        # Get usage breakdown by trace type
        usage_breakdown = (
            db.query(
                TraceJob.type,
                func.count(TraceJob.id).label('queues'),
                func.sum(TraceJob.credits_used).label('credits_used')
            )
            .filter(TraceJob.user_id == user.id)
            .group_by(TraceJob.type)
            .all()
        )
        
        # Format usage breakdown
        breakdown_dict = {
            "normal": {"queues": 0, "credits_used": 0},
            "enhanced": {"queues": 0, "credits_used": 0}
        }
        
        for breakdown in usage_breakdown:
            breakdown_dict[breakdown.type] = {
                "queues": breakdown.queues or 0,
                "credits_used": breakdown.credits_used or 0
            }
        
        # Get credit stats
        credit_service = CreditService(db)
        credit_stats = credit_service.get_credit_stats(user.id)
        
        # Get recent activity
        recent_jobs = (
            db.query(TraceJob)
            .filter(TraceJob.user_id == user.id)
            .order_by(desc(TraceJob.created_at))
            .limit(5)
            .all()
        )
        
        # Get monthly statistics (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_stats = (
            db.query(
                func.count(TraceJob.id).label('monthly_jobs'),
                func.sum(TraceJob.total_records).label('monthly_properties'),
                func.sum(TraceJob.credits_used).label('monthly_credits_used')
            )
            .filter(
                TraceJob.user_id == user.id,
                TraceJob.created_at >= thirty_days_ago
            )
            .first()
        )
        
        return {
            "lists_uploaded": trace_stats.total_jobs or 0,
            "properties_uploaded": trace_stats.total_properties or 0,
            "successful_traces": trace_stats.successful_traces or 0,
            "total_credits_used": trace_stats.total_credits_used or 0,
            "effective_rate": float(credit_stats.effective_rate_per_credit),
            "usage_breakdown": breakdown_dict,
            "credit_balance": credit_stats.current_balance,
            "monthly_stats": {
                "lists_uploaded": monthly_stats.monthly_jobs or 0,
                "properties_uploaded": monthly_stats.monthly_properties or 0,
                "credits_used": monthly_stats.monthly_credits_used or 0
            },
            "recent_activity": [
                {
                    "id": job.id,
                    "name": job.name,
                    "type": job.type,
                    "status": job.status,
                    "created_at": job.created_at,
                    "credits_used": job.credits_used
                }
                for job in recent_jobs
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )


@router.get("/activity")
async def get_recent_activity(
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Any:
    """Get recent user activity"""
    user = get_current_user(request)
    
    try:
        # Get recent trace jobs
        recent_traces = (
            db.query(TraceJob)
            .filter(TraceJob.user_id == user.id)
            .order_by(desc(TraceJob.created_at))
            .limit(limit)
            .all()
        )
        
        # Get recent manual searches
        recent_searches = (
            db.query(ManualSearch)
            .filter(ManualSearch.user_id == user.id)
            .order_by(desc(ManualSearch.created_at))
            .limit(limit)
            .all()
        )
        
        # Get recent credit transactions
        recent_transactions = (
            db.query(CreditTransaction)
            .filter(CreditTransaction.user_id == user.id)
            .order_by(desc(CreditTransaction.created_at))
            .limit(limit)
            .all()
        )
        
        # Combine and sort by date
        activity = []
        
        for trace in recent_traces:
            activity.append({
                "type": "trace_job",
                "id": trace.id,
                "title": f"Trace Job: {trace.name}",
                "description": f"{trace.type.value} trace with {trace.total_records} records",
                "status": trace.status.value,
                "created_at": trace.created_at,
                "credits_used": trace.credits_used
            })
        
        for search in recent_searches:
            activity.append({
                "type": "manual_search",
                "id": search.id,
                "title": f"Manual Search: {search.search_type.value}",
                "description": search.search_query,
                "status": search.status.value,
                "created_at": search.created_at,
                "credits_used": search.credits_used
            })
        
        for transaction in recent_transactions:
            activity.append({
                "type": "credit_transaction",
                "id": transaction.id,
                "title": f"Credit {transaction.transaction_type.value}",
                "description": transaction.description or "",
                "status": "completed",
                "created_at": transaction.created_at,
                "credits_used": abs(transaction.amount)
            })
        
        # Sort by created_at descending
        activity.sort(key=lambda x: x["created_at"], reverse=True)
        
        return activity[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent activity"
        )


@router.get("/analytics")
async def get_analytics(
    request: Request,
    days: int = 30,
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed analytics data"""
    user = get_current_user(request)
    
    try:
        # Date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily trace statistics
        daily_stats = (
            db.query(
                func.date(TraceJob.created_at).label('date'),
                func.count(TraceJob.id).label('jobs_created'),
                func.sum(TraceJob.total_records).label('records_processed'),
                func.sum(TraceJob.credits_used).label('credits_used')
            )
            .filter(
                TraceJob.user_id == user.id,
                TraceJob.created_at >= start_date,
                TraceJob.created_at <= end_date
            )
            .group_by(func.date(TraceJob.created_at))
            .order_by(func.date(TraceJob.created_at))
            .all()
        )
        
        # Success rate by trace type
        success_rates = (
            db.query(
                TraceJob.type,
                func.count(TraceJob.id).label('total_jobs'),
                func.sum(
                    func.case(
                        (TraceJob.status == TraceJobStatus.COMPLETED, 1),
                        else_=0
                    )
                ).label('completed_jobs')
            )
            .filter(TraceJob.user_id == user.id)
            .group_by(TraceJob.type)
            .all()
        )
        
        # Format success rates
        formatted_success_rates = {}
        for rate in success_rates:
            success_rate = (rate.completed_jobs / rate.total_jobs * 100) if rate.total_jobs > 0 else 0
            formatted_success_rates[rate.type.value] = {
                "total_jobs": rate.total_jobs,
                "completed_jobs": rate.completed_jobs,
                "success_rate": round(success_rate, 2)
            }
        
        # Credit usage over time
        credit_usage = (
            db.query(
                func.date(CreditTransaction.created_at).label('date'),
                func.sum(
                    func.case(
                        (CreditTransaction.transaction_type == CreditTransactionType.USAGE, func.abs(CreditTransaction.amount)),
                        else_=0
                    )
                ).label('credits_used'),
                func.sum(
                    func.case(
                        (CreditTransaction.transaction_type.in_([CreditTransactionType.PURCHASE, CreditTransactionType.BONUS]), CreditTransaction.amount),
                        else_=0
                    )
                ).label('credits_purchased')
            )
            .filter(
                CreditTransaction.user_id == user.id,
                CreditTransaction.created_at >= start_date,
                CreditTransaction.created_at <= end_date
            )
            .group_by(func.date(CreditTransaction.created_at))
            .order_by(func.date(CreditTransaction.created_at))
            .all()
        )
        
        return {
            "daily_stats": [
                {
                    "date": stat.date.isoformat(),
                    "jobs_created": stat.jobs_created or 0,
                    "records_processed": stat.records_processed or 0,
                    "credits_used": stat.credits_used or 0
                }
                for stat in daily_stats
            ],
            "success_rates": formatted_success_rates,
            "credit_usage": [
                {
                    "date": usage.date.isoformat(),
                    "credits_used": usage.credits_used or 0,
                    "credits_purchased": usage.credits_purchased or 0
                }
                for usage in credit_usage
            ],
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics data"
        )
