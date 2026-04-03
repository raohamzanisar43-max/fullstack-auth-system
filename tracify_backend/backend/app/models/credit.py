"""
Credit system models for Tracerfy Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, DECIMAL, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class CreditTransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"


class CreditPackage(Base):
    __tablename__ = "credit_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    credits = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    bonus_credits = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CreditBalance(Base):
    __tablename__ = "credit_balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_credits = Column(Integer, default=0, nullable=False)
    total_purchased = Column(Integer, default=0, nullable=False)
    total_used = Column(Integer, default=0, nullable=False)
    total_bonus = Column(Integer, default=0, nullable=False)
    effective_rate = Column(DECIMAL(10, 4), default=0.0200, nullable=False)  # $0.02 per credit
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="credit_balance")
    transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(Enum(CreditTransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for purchases/bonus, negative for usage/refund
    balance_after = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(255), nullable=True)  # Can reference trace jobs, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(String(255), primary_key=True)  # Stripe payment intent ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(50), nullable=False)  # pending, completed, failed, refunded
    payment_method_id = Column(String(255), nullable=True)
    package_id = Column(Integer, ForeignKey("credit_packages.id"), nullable=True)
    credits_purchased = Column(Integer, nullable=False)
    bonus_credits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    package = relationship("CreditPackage")
