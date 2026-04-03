"""
Credit system schemas for Tracerfy Backend
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class CreditTransactionType(str, Enum):
    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"


class CreditPackage(BaseModel):
    id: int
    name: str
    credits: int
    price: Decimal
    description: Optional[str] = None
    bonus_credits: int = 0
    is_active: bool = True
    
    class Config:
        from_attributes = True


class CreditBalance(BaseModel):
    user_id: int
    current_credits: int
    total_purchased: int
    total_used: int
    total_bonus: int
    effective_rate: Decimal
    last_updated: datetime
    
    class Config:
        from_attributes = True


class CreditTransaction(BaseModel):
    id: int
    user_id: int
    transaction_type: CreditTransactionType
    amount: int
    balance_after: int
    description: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditPurchase(BaseModel):
    package_id: int
    payment_method_id: str
    amount: Decimal
    currency: str = "USD"


class CreditPurchaseResponse(BaseModel):
    transaction_id: str
    credits_added: int
    bonus_credits: int
    total_credits: int
    new_balance: int
    amount_charged: Decimal
    currency: str


class CreditUsage(BaseModel):
    amount: int
    description: Optional[str] = None
    reference_id: Optional[str] = None


class CreditUsageResponse(BaseModel):
    transaction_id: str
    credits_used: int
    new_balance: int
    description: str


class CreditTransactionHistory(BaseModel):
    transactions: List[CreditTransaction]
    total_count: int
    page: int
    per_page: int


class CreditStats(BaseModel):
    current_balance: int
    total_purchased: int
    total_used: int
    total_bonus: int
    effective_rate_per_credit: Decimal
    last_purchase_date: Optional[datetime] = None
    last_usage_date: Optional[datetime] = None
    usage_this_month: int
    purchases_this_month: int
