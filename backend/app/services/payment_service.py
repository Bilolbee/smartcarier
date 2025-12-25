"""
=============================================================================
PAYMENT SERVICE - Stripe Integration
=============================================================================

Bu service to'lovlarni boshqaradi:
- Stripe payment integratsiya
- Premium subscription
- Webhook handling
- Payment logging va security

Xususiyatlari:
- Idempotency (double payment prevention)
- Webhook signature verification
- Payment status tracking
- Refund support

AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import logging
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.payment import Payment as PaymentModel
from app.models.user import User

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS
# =============================================================================

class PaymentProvider(str, Enum):
    """Payment providers."""
    STRIPE = "stripe"
    PAYME = "payme"
    CLICK = "click"


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionTier(str, Enum):
    """Subscription tiers."""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


# =============================================================================
# MODELS
# =============================================================================

class PaymentLog(BaseModel):
    """Payment log entry."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Payment info
    provider: PaymentProvider
    provider_payment_id: Optional[str] = None  # Stripe payment_intent_id, etc.
    status: PaymentStatus
    
    # User info
    user_id: str
    user_email: str
    
    # Amount
    amount: int  # in cents
    currency: str = "USD"
    
    # Subscription
    subscription_tier: SubscriptionTier
    subscription_months: int = 1
    
    # Idempotency
    idempotency_key: str
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Error tracking
    error_message: Optional[str] = None
    error_code: Optional[str] = None


# =============================================================================
# PAYMENT SERVICE
# =============================================================================

class PaymentService:
    """
    Payment processing service.
    
    Supports multiple payment providers with secure handling.
    """
    
    def __init__(self):
        """Initialize payment service."""
        self.stripe_secret_key = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
        self.stripe_webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or ""
        
        # In-memory payment logs (production: database)
        self._payment_logs: Dict[str, PaymentLog] = {}
        
        # Idempotency tracking (production: Redis)
        self._processed_payments: Dict[str, str] = {}  # {idempotency_key: payment_id}
        
        logger.info("PaymentService initialized")
    
    # =========================================================================
    # STRIPE INTEGRATION
    # =========================================================================
    
    async def create_stripe_payment_intent(
        self,
        db: Optional[Session],
        user_id: str,
        user_email: str,
        amount: int,
        currency: str,
        subscription_tier: SubscriptionTier,
        subscription_months: int,
        idempotency_key: str,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create Stripe payment intent.
        
        Args:
            user_id: User ID
            user_email: User email
            amount: Amount in cents
            currency: Currency code
            subscription_tier: Subscription tier
            subscription_months: Number of months
            idempotency_key: Unique key to prevent double payment
            ip_address: Client IP
            metadata: Additional metadata
            
        Returns:
            Payment intent data with client_secret
        """
        # Check idempotency (DB preferred)
        if db:
            existing = db.query(PaymentModel).filter(PaymentModel.idempotency_key == idempotency_key).first()
            if existing:
                raise ValueError("Duplicate payment attempt (idempotency_key already used)")
        else:
            if idempotency_key in self._processed_payments:
                existing_payment_id = self._processed_payments[idempotency_key]
                logger.warning(f"Duplicate payment attempt blocked: {idempotency_key}")
                raise ValueError(f"Payment already processed: {existing_payment_id}")
        
        try:
            # Create DB record first (audit trail)
            payment_db_id: Optional[str] = None
            if db:
                payment = PaymentModel(
                    provider=PaymentProvider.STRIPE.value,
                    provider_payment_id=None,
                    status=PaymentStatus.PENDING.value,
                    user_id=UUID(user_id),
                    amount=amount,
                    currency=currency,
                    subscription_tier=subscription_tier.value,
                    subscription_months=subscription_months,
                    idempotency_key=idempotency_key,
                    ip_address=ip_address,
                    user_agent=(metadata or {}).get("user_agent") if metadata else None,
                )
                db.add(payment)
                db.commit()
                db.refresh(payment)
                payment_db_id = str(payment.id)
            
            # Mock implementation for development
            if not self.stripe_secret_key:
                logger.warning("Stripe not configured, using mock payment")
                
                payment_intent_id = f"pi_mock_{uuid4().hex[:16]}"
                client_secret = f"{payment_intent_id}_secret_{uuid4().hex[:16]}"
                
                # Create payment log
                payment_log = PaymentLog(
                    provider=PaymentProvider.STRIPE,
                    provider_payment_id=payment_intent_id,
                    status=PaymentStatus.PENDING,
                    user_id=user_id,
                    user_email=user_email,
                    amount=amount,
                    currency=currency,
                    subscription_tier=subscription_tier,
                    subscription_months=subscription_months,
                    idempotency_key=idempotency_key,
                    ip_address=ip_address,
                    metadata=metadata,
                )
                
                self._payment_logs[payment_log.id] = payment_log
                self._processed_payments[idempotency_key] = payment_log.id

                # Also store in DB if available
                if db and payment_db_id:
                    payment = db.query(PaymentModel).filter(PaymentModel.id == UUID(payment_db_id)).first()
                    if payment:
                        payment.provider_payment_id = payment_intent_id
                        payment.status = PaymentStatus.PENDING.value
                        db.commit()
                
                logger.info(f"Mock payment intent created: {payment_intent_id} for user {user_id}")
                
                return {
                    "payment_id": payment_db_id or payment_log.id,
                    "payment_intent_id": payment_intent_id,
                    "client_secret": client_secret,
                    "status": "requires_payment_method",
                    "amount": amount,
                    "currency": currency,
                }

            # Real Stripe implementation
            import stripe  # type: ignore
            stripe.api_key = self.stripe_secret_key

            stripe_metadata = {
                "user_id": user_id,
                "subscription_tier": subscription_tier.value,
                "subscription_months": str(subscription_months),
            }
            if payment_db_id:
                stripe_metadata["payment_id"] = payment_db_id
            if metadata:
                # Keep it small; Stripe metadata values must be strings
                for k, v in metadata.items():
                    if v is None:
                        continue
                    stripe_metadata[f"meta_{k}"] = str(v)[:200]

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency.lower(),
                automatic_payment_methods={"enabled": True},
                metadata=stripe_metadata,
                idempotency_key=idempotency_key,
            )

            payment_intent_id = payment_intent["id"]
            client_secret = payment_intent["client_secret"]

            if db and payment_db_id:
                payment = db.query(PaymentModel).filter(PaymentModel.id == UUID(payment_db_id)).first()
                if payment:
                    payment.provider_payment_id = payment_intent_id
                    payment.status = PaymentStatus.PROCESSING.value
                    db.commit()

            return {
                "payment_id": payment_db_id or (payment_intent_id),
                "payment_intent_id": payment_intent_id,
                "client_secret": client_secret,
                "status": payment_intent.get("status", "requires_payment_method"),
                "amount": amount,
                "currency": currency,
            }
            
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            
            # Log error
            error_log = PaymentLog(
                provider=PaymentProvider.STRIPE,
                status=PaymentStatus.FAILED,
                user_id=user_id,
                user_email=user_email,
                amount=amount,
                currency=currency,
                subscription_tier=subscription_tier,
                subscription_months=subscription_months,
                idempotency_key=idempotency_key,
                error_message=str(e),
                error_code="PAYMENT_INTENT_CREATION_FAILED",
            )
            self._payment_logs[error_log.id] = error_log
            
            raise
    
    async def handle_stripe_webhook(
        self,
        db: Optional[Session],
        payload: bytes,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook event.
        
        Verifies signature and processes event.
        
        Args:
            payload: Webhook payload (raw bytes)
            signature: Stripe signature header
            
        Returns:
            Processing result
        """
        try:
            # Verify signature and parse event (Stripe SDK preferred)
            event = None
            if not self.stripe_webhook_secret:
                if settings.PAYMENTS_REQUIRE_WEBHOOK_SECRET and not settings.DEBUG:
                    raise ValueError("Stripe webhook secret not configured")
            try:
                import stripe  # type: ignore
                if self.stripe_webhook_secret:
                    event = stripe.Webhook.construct_event(payload, signature, self.stripe_webhook_secret)
                else:
                    event = json.loads(payload.decode("utf-8"))
            except Exception:
                # Fallback to legacy verification (dev only)
                if not self._verify_stripe_signature(payload, signature):
                    logger.error("Invalid Stripe webhook signature")
                    raise ValueError("Invalid signature")
                event = json.loads(payload.decode("utf-8"))

            event_type = event.get("type")
            event_data = event.get("data", {}).get("object", {})
            
            logger.info(f"Stripe webhook received: {event_type}")
            
            # Handle different event types
            if event_type == 'payment_intent.succeeded':
                return await self._handle_payment_success(db, event_data)
            
            elif event_type == 'payment_intent.payment_failed':
                return await self._handle_payment_failure(db, event_data)
            
            elif event_type == 'charge.refunded':
                return await self._handle_refund(db, event_data)
            
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {"status": "ignored", "event_type": event_type}
            
        except Exception as e:
            logger.exception(f"Webhook processing error: {e}")
            raise
    
    def _verify_stripe_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature.
        
        Critical security measure to prevent fake webhooks.
        """
        if not self.stripe_webhook_secret:
            logger.warning("Stripe webhook secret not configured")
            return settings.DEBUG  # only allow skipping in dev
        
        try:
            # Extract timestamp and signature
            parts = signature.split(',')
            timestamp = None
            signatures = []
            
            for part in parts:
                if part.startswith('t='):
                    timestamp = part[2:]
                elif part.startswith('v1='):
                    signatures.append(part[3:])
            
            if not timestamp or not signatures:
                return False
            
            # Create signed payload
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            
            # Compute expected signature
            expected_signature = hmac.new(
                self.stripe_webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare
            return any(
                hmac.compare_digest(expected_signature, sig)
                for sig in signatures
            )
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    async def _handle_payment_success(self, db: Optional[Session], payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment."""
        payment_intent_id = payment_data.get('id')
        amount = payment_data.get('amount')
        metadata = payment_data.get('metadata', {})
        
        user_id = metadata.get('user_id')
        subscription_tier = metadata.get('subscription_tier', 'premium')
        subscription_months = int(metadata.get("subscription_months", "1") or 1)
        
        logger.info(f"Payment succeeded: {payment_intent_id} for user {user_id}")
        
        # Update payment log
        for payment_log in self._payment_logs.values():
            if payment_log.provider_payment_id == payment_intent_id:
                payment_log.status = PaymentStatus.COMPLETED
                break

        # Update DB payment + user subscription (production)
        if db and user_id:
            payment = db.query(PaymentModel).filter(PaymentModel.provider_payment_id == payment_intent_id).first()
            if payment:
                payment.status = PaymentStatus.COMPLETED.value
                db.add(payment)
            user = db.query(User).filter(User.id == UUID(user_id), User.is_deleted == False).first()
            if user:
                now = datetime.now(timezone.utc)
                base = user.subscription_expires_at if getattr(user, "subscription_expires_at", None) and user.subscription_expires_at > now else now
                user.subscription_tier = subscription_tier
                user.subscription_expires_at = base + timedelta(days=30 * subscription_months)
                db.add(user)
            db.commit()
        
        # Here you would:
        # 1. Update user's subscription status in database
        # 2. Send confirmation email
        # 3. Log to analytics
        
        return {
            "status": "success",
            "payment_intent_id": payment_intent_id,
            "user_id": user_id,
        }
    
    async def _handle_payment_failure(self, db: Optional[Session], payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment."""
        payment_intent_id = payment_data.get('id')
        error = payment_data.get('last_payment_error', {})
        
        logger.error(f"Payment failed: {payment_intent_id} - {error}")
        
        # Update payment log
        for payment_log in self._payment_logs.values():
            if payment_log.provider_payment_id == payment_intent_id:
                payment_log.status = PaymentStatus.FAILED
                payment_log.error_message = error.get('message')
                payment_log.error_code = error.get('code')
                break

        if db:
            payment = db.query(PaymentModel).filter(PaymentModel.provider_payment_id == payment_intent_id).first()
            if payment:
                payment.status = PaymentStatus.FAILED.value
                payment.error_message = error.get("message")
                payment.error_code = error.get("code")
                db.commit()
        
        return {
            "status": "failed",
            "payment_intent_id": payment_intent_id,
            "error": error,
        }
    
    async def _handle_refund(self, db: Optional[Session], charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund."""
        charge_id = charge_data.get('id')
        amount_refunded = charge_data.get('amount_refunded')
        
        logger.info(f"Refund processed: {charge_id} - ${amount_refunded/100:.2f}")
        
        # Update payment log
        for payment_log in self._payment_logs.values():
            if payment_log.provider_payment_id == charge_id:
                payment_log.status = PaymentStatus.REFUNDED
                break

        if db:
            payment = db.query(PaymentModel).filter(PaymentModel.provider_payment_id == charge_id).first()
            if payment:
                payment.status = PaymentStatus.REFUNDED.value
                db.commit()
        
        return {
            "status": "refunded",
            "charge_id": charge_id,
            "amount_refunded": amount_refunded,
        }
    
    # =========================================================================
    # QUERY METHODS
    # =========================================================================
    
    def get_payment_logs(
        self,
        user_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        limit: int = 100,
    ) -> list[PaymentLog]:
        """Get payment logs with filters."""
        logs = list(self._payment_logs.values())
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if status:
            logs = [log for log in logs if log.status == status]
        
        # Sort by created_at (newest first)
        logs.sort(key=lambda x: x.created_at, reverse=True)
        
        return logs[:limit]
    
    def get_payment_by_id(self, payment_id: str) -> Optional[PaymentLog]:
        """Get payment log by ID."""
        return self._payment_logs.get(payment_id)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

payment_service = PaymentService()


# =============================================================================
# SUBSCRIPTION PRICING
# =============================================================================

SUBSCRIPTION_PRICING = {
    SubscriptionTier.PREMIUM: {
        "monthly": 999,  # $9.99 in cents
        "quarterly": 2499,  # $24.99
        "yearly": 8999,  # $89.99
        "features": [
            "Unlimited AI resume generation",
            "Priority job matching",
            "Advanced analytics",
            "Premium templates",
            "Email support",
        ],
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly": 4999,  # $49.99
        "features": [
            "Everything in Premium",
            "Custom branding",
            "API access",
            "Dedicated support",
            "Team management",
        ],
    },
}


def get_subscription_price(tier: SubscriptionTier, months: int = 1) -> int:
    """
    Get subscription price in cents.
    
    Args:
        tier: Subscription tier
        months: Number of months (1, 3, or 12)
        
    Returns:
        Price in cents
    """
    pricing = SUBSCRIPTION_PRICING.get(tier, {})
    
    if months == 1:
        return pricing.get("monthly", 0)
    elif months == 3:
        return pricing.get("quarterly", pricing.get("monthly", 0) * 3)
    elif months == 12:
        return pricing.get("yearly", pricing.get("monthly", 0) * 12)
    else:
        # Custom duration
        return pricing.get("monthly", 0) * months









