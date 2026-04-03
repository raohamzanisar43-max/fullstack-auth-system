"""
Payment Gateway Integration
Handles Stripe payments for credit purchases
"""

import stripe
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import PaymentError


class PaymentGateway:
    """Stripe payment gateway integration"""
    
    def __init__(self):
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("STRIPE_SECRET_KEY not configured")
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        user_id: int,
        credits: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> stripe.PaymentIntent:
        """Create a payment intent for credit purchase"""
        try:
            # Convert to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)
            
            intent_metadata = {
                "user_id": str(user_id),
                "credits": str(credits),
                "type": "credit_purchase"
            }
            
            if metadata:
                intent_metadata.update(metadata)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                metadata=intent_metadata,
                automatic_payment_methods={
                    "enabled": True,
                },
                description=f"Purchase {credits} credits"
            )
            
            return payment_intent
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Payment intent creation failed: {str(e)}")
    
    async def confirm_payment(self, payment_intent_id: str) -> stripe.PaymentIntent:
        """Confirm and retrieve payment intent status"""
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise PaymentError(f"Payment confirmation failed: {str(e)}")
    
    async def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> stripe.Refund:
        """Create refund for a payment"""
        try:
            refund_params = {
                "payment_intent": payment_intent_id
            }
            
            if amount:
                refund_params["amount"] = int(amount * 100)
            
            if reason:
                refund_params["reason"] = reason
            
            return stripe.Refund.create(**refund_params)
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Refund creation failed: {str(e)}")
    
    async def get_payment_methods(self, customer_id: str) -> list:
        """Get saved payment methods for a customer"""
        try:
            return stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
        except stripe.error.StripeError as e:
            raise PaymentError(f"Failed to retrieve payment methods: {str(e)}")
    
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> stripe.Customer:
        """Create a Stripe customer"""
        try:
            customer_params = {
                "email": email
            }
            
            if name:
                customer_params["name"] = name
            
            if metadata:
                customer_params["metadata"] = metadata
            
            return stripe.Customer.create(**customer_params)
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Customer creation failed: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            stripe.WebhookSignature.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except stripe.error.SignatureVerificationError:
            return False
    
    async def handle_webhook_event(self, payload: str) -> Dict[str, Any]:
        """Process incoming webhook events"""
        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
            
            return {
                "type": event.type,
                "data": event.data,
                "id": event.id
            }
            
        except Exception as e:
            raise PaymentError(f"Webhook processing failed: {str(e)}")
    
    async def get_customer_payment_history(
        self,
        customer_id: str,
        limit: int = 10
    ) -> list:
        """Get payment history for a customer"""
        try:
            charges = stripe.Charge.list(
                customer=customer_id,
                limit=limit
            )
            
            return charges.data
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Failed to retrieve payment history: {str(e)}")


# Singleton instance
payment_gateway = PaymentGateway() if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY else None


class CreditPricing:
    """Credit pricing tiers and calculations"""
    
    # Pricing tiers (credits, price_per_credit)
    PRICING_TIERS = [
        (1000, 0.02),    # $0.02 per credit for 1000 credits
        (2500, 0.018),   # $0.018 per credit for 2500 credits  
        (5000, 0.015),   # $0.015 per credit for 5000 credits
        (10000, 0.012),  # $0.012 per credit for 10000 credits
        (25000, 0.01),   # $0.01 per credit for 25000+ credits
    ]
    
    @classmethod
    def calculate_price(cls, credits: int) -> Decimal:
        """Calculate price based on credit quantity"""
        for tier_credits, price_per_credit in cls.PRICING_TIERS:
            if credits >= tier_credits:
                return Decimal(credits) * Decimal(str(price_per_credit))
        
        # Default pricing for small quantities
        return Decimal(credits) * Decimal("0.025")
    
    @classmethod
    def get_best_tier(cls, credits: int) -> Dict[str, Any]:
        """Get the best pricing tier for given credit amount"""
        for tier_credits, price_per_credit in cls.PRICING_TIERS:
            if credits >= tier_credits:
                return {
                    "credits": credits,
                    "price_per_credit": price_per_credit,
                    "total_price": float(cls.calculate_price(credits))
                }
        
        return {
            "credits": credits,
            "price_per_credit": 0.025,
            "total_price": float(cls.calculate_price(credits))
        }
    
    @classmethod
    def get_all_tiers(cls) -> list:
        """Get all available pricing tiers"""
        return [
            {
                "min_credits": tier_credits,
                "price_per_credit": price_per_credit,
                "example_total": float(tier_credits * price_per_credit)
            }
            for tier_credits, price_per_credit in cls.PRICING_TIERS
        ]
