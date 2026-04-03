"""
Credit system service for Tracerfy Backend
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from decimal import Decimal

from app.models.credit import (
    CreditBalance, CreditTransaction, CreditPackage, PaymentTransaction,
    CreditTransactionType
)
from app.models.user import User
from app.schemas.credit import (
    CreditPurchase, CreditPurchaseResponse, CreditUsage, CreditUsageResponse,
    CreditStats, CreditTransactionHistory
)
from app.core.exceptions import ValidationError, NotFoundError
from app.core.config import settings


class CreditService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_balance(self, user_id: int) -> CreditBalance:
        """Get user's credit balance"""
        balance = (
            self.db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
        )
        
        if not balance:
            # Create initial balance for new user
            balance = CreditBalance(
                user_id=user_id,
                current_credits=0,
                total_purchased=0,
                total_used=0,
                total_bonus=0,
                effective_rate=Decimal('0.0200')
            )
            self.db.add(balance)
            self.db.commit()
            self.db.refresh(balance)
        
        return balance

    def purchase_credits(self, user_id: int, purchase_data: CreditPurchase) -> CreditPurchaseResponse:
        """Purchase credits using payment method"""
        
        # Get package details
        package = (
            self.db.query(CreditPackage)
            .filter(CreditPackage.id == purchase_data.package_id, CreditPackage.is_active == True)
            .first()
        )
        
        if not package:
            raise NotFoundError("Credit package not found")
        
        # TODO: Process payment with Stripe
        # payment_result = self._process_payment(purchase_data.payment_method_id, package.price)
        payment_result = {"status": "completed", "transaction_id": f"pi_{datetime.utcnow().timestamp()}"}
        
        if payment_result["status"] != "completed":
            raise ValidationError("Payment failed")
        
        # Get or create user balance
        balance = self.get_user_balance(user_id)
        
        # Calculate total credits (including bonus)
        total_credits = package.credits + package.bonus_credits
        
        # Update balance
        balance.current_credits += total_credits
        balance.total_purchased += package.credits
        balance.total_bonus += package.bonus_credits
        balance.last_updated = datetime.utcnow()
        
        # Create transaction record
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.PURCHASE,
            amount=package.credits,
            balance_after=balance.current_credits,
            description=f"Purchased {package.name} package",
            reference_id=payment_result["transaction_id"]
        )
        
        # Add bonus transaction if applicable
        if package.bonus_credits > 0:
            bonus_transaction = CreditTransaction(
                user_id=user_id,
                transaction_type=CreditTransactionType.BONUS,
                amount=package.bonus_credits,
                balance_after=balance.current_credits,
                description=f"Bonus credits from {package.name} package",
                reference_id=payment_result["transaction_id"]
            )
            self.db.add(bonus_transaction)
        
        # Create payment transaction record
        payment_transaction = PaymentTransaction(
            id=payment_result["transaction_id"],
            user_id=user_id,
            amount=package.price,
            currency=purchase_data.currency,
            status="completed",
            payment_method_id=purchase_data.payment_method_id,
            package_id=package.id,
            credits_purchased=package.credits,
            bonus_credits=package.bonus_credits
        )
        
        self.db.add(transaction)
        self.db.add(payment_transaction)
        self.db.commit()
        self.db.refresh(balance)
        
        return CreditPurchaseResponse(
            transaction_id=payment_result["transaction_id"],
            credits_added=package.credits,
            bonus_credits=package.bonus_credits,
            total_credits=total_credits,
            new_balance=balance.current_credits,
            amount_charged=package.price,
            currency=purchase_data.currency
        )

    def use_credits(self, user_id: int, usage_data: CreditUsage) -> CreditUsageResponse:
        """Use credits for services"""
        
        balance = self.get_user_balance(user_id)
        
        if balance.current_credits < usage_data.amount:
            raise ValidationError(f"Insufficient credits. Available: {balance.current_credits}, Required: {usage_data.amount}")
        
        # Deduct credits
        balance.current_credits -= usage_data.amount
        balance.total_used += usage_data.amount
        balance.last_updated = datetime.utcnow()
        
        # Create transaction record
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.USAGE,
            amount=-usage_data.amount,  # Negative for usage
            balance_after=balance.current_credits,
            description=usage_data.description or "Credits used",
            reference_id=usage_data.reference_id
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(balance)
        
        return CreditUsageResponse(
            transaction_id=str(transaction.id),
            credits_used=usage_data.amount,
            new_balance=balance.current_credits,
            description=transaction.description
        )

    def get_transaction_history(self, user_id: int, skip: int = 0, limit: int = 50) -> CreditTransactionHistory:
        """Get user's credit transaction history"""
        
        # Get transactions
        transactions = (
            self.db.query(CreditTransaction)
            .filter(CreditTransaction.user_id == user_id)
            .order_by(desc(CreditTransaction.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Get total count
        total_count = (
            self.db.query(CreditTransaction)
            .filter(CreditTransaction.user_id == user_id)
            .count()
        )
        
        return CreditTransactionHistory(
            transactions=transactions,
            total_count=total_count,
            page=skip // limit + 1,
            per_page=limit
        )

    def get_credit_stats(self, user_id: int) -> CreditStats:
        """Get user's credit statistics"""
        
        balance = self.get_user_balance(user_id)
        
        # Get this month's usage and purchases
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = (
            self.db.query(func.sum(CreditTransaction.amount))
            .filter(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type == CreditTransactionType.USAGE,
                CreditTransaction.created_at >= current_month_start
            )
            .scalar() or 0
        )
        
        monthly_purchases = (
            self.db.query(func.sum(CreditTransaction.amount))
            .filter(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type.in_([CreditTransactionType.PURCHASE, CreditTransactionType.BONUS]),
                CreditTransaction.created_at >= current_month_start
            )
            .scalar() or 0
        )
        
        # Get last purchase and usage dates
        last_purchase = (
            self.db.query(CreditTransaction.created_at)
            .filter(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type == CreditTransactionType.PURCHASE
            )
            .order_by(desc(CreditTransaction.created_at))
            .first()
        )
        
        last_usage = (
            self.db.query(CreditTransaction.created_at)
            .filter(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type == CreditTransactionType.USAGE
            )
            .order_by(desc(CreditTransaction.created_at))
            .first()
        )
        
        # Calculate effective rate
        effective_rate = Decimal('0.0200')  # Default rate
        if balance.total_purchased > 0:
            # Calculate from actual payment data
            total_spent = (
                self.db.query(func.sum(PaymentTransaction.amount))
                .filter(PaymentTransaction.user_id == user_id, PaymentTransaction.status == "completed")
                .scalar() or Decimal('0.00')
            )
            if total_spent > 0:
                effective_rate = total_spent / Decimal(balance.total_purchased)
        
        return CreditStats(
            current_balance=balance.current_credits,
            total_purchased=balance.total_purchased,
            total_used=balance.total_used,
            total_bonus=balance.total_bonus,
            effective_rate_per_credit=effective_rate,
            last_purchase_date=last_purchase[0] if last_purchase else None,
            last_usage_date=last_usage[0] if last_usage else None,
            usage_this_month=abs(monthly_usage),
            purchases_this_month=monthly_purchases
        )

    def get_available_packages(self) -> List[CreditPackage]:
        """Get available credit packages"""
        return (
            self.db.query(CreditPackage)
            .filter(CreditPackage.is_active == True)
            .order_by(CreditPackage.price)
            .all()
        )

    def refund_credits(self, user_id: int, amount: int, reason: str, reference_id: Optional[str] = None) -> CreditTransaction:
        """Refund credits to user"""
        
        balance = self.get_user_balance(user_id)
        
        # Add credits back
        balance.current_credits += amount
        balance.total_used -= amount  # Reduce total used
        balance.last_updated = datetime.utcnow()
        
        # Create refund transaction
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.REFUND,
            amount=amount,
            balance_after=balance.current_credits,
            description=f"Refund: {reason}",
            reference_id=reference_id
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction

    def _process_payment(self, payment_method_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process payment with Stripe"""
        # TODO: Implement Stripe payment processing
        # This is a placeholder implementation
        return {
            "status": "completed",
            "transaction_id": f"pi_{datetime.utcnow().timestamp()}"
        }
