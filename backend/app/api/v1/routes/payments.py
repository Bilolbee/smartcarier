"""
=============================================================================
PAYMENT ENDPOINTS
=============================================================================

Handles subscription payments and billing.

ENDPOINTS:
    POST /create-payment-intent   - Create payment intent
    POST /webhook/stripe           - Stripe webhook
    GET  /my-payments              - Get user's payment history
    GET  /pricing                  - Get subscription pricing

AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import logging
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.dependencies import get_db, get_current_active_user
from app.models import User
from app.services.payment_service import (
    payment_service,
    PaymentProvider,
    SubscriptionTier,
    SUBSCRIPTION_PRICING,
    get_subscription_price,
)

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CreatePaymentIntentRequest(BaseModel):
    """Request to create payment intent."""
    
    subscription_tier: str = Field(
        ...,
        description="Subscription tier: premium or enterprise"
    )
    subscription_months: int = Field(
        default=1,
        ge=1,
        le=12,
        description="Number of months (1-12)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "subscription_tier": "premium",
                "subscription_months": 1
            }
        }


class PaymentIntentResponse(BaseModel):
    """Payment intent response."""
    
    success: bool
    payment_id: str
    client_secret: str
    amount: int
    currency: str
    subscription_tier: str
    subscription_months: int


class PaymentHistoryResponse(BaseModel):
    """Payment history response."""
    
    success: bool
    payments: list
    total: int


class PricingResponse(BaseModel):
    """Subscription pricing response."""
    
    success: bool
    pricing: dict


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/create-payment-intent",
    response_model=PaymentIntentResponse,
    summary="Create payment intent",
    description="Create a Stripe payment intent for subscription"
)
async def create_payment_intent(
    request_data: CreatePaymentIntentRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create payment intent for subscription."""
    
    try:
        # Validate subscription tier
        try:
            tier = SubscriptionTier(request_data.subscription_tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subscription tier: {request_data.subscription_tier}"
            )
        
        # Get price
        amount = get_subscription_price(tier, request_data.subscription_months)
        
        if amount == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subscription configuration"
            )
        
        # Generate idempotency key
        idempotency_key = f"{current_user.id}_{tier.value}_{request_data.subscription_months}_{uuid4().hex[:8]}"
        
        # Get client IP
        client_ip = request.client.host if request.client else None
        
        # Create payment intent
        payment_intent = await payment_service.create_stripe_payment_intent(
            user_id=str(current_user.id),
            user_email=current_user.email,
            amount=amount,
            currency="USD",
            subscription_tier=tier,
            subscription_months=request_data.subscription_months,
            idempotency_key=idempotency_key,
            ip_address=client_ip,
            metadata={
                "user_name": current_user.full_name,
                "user_role": current_user.role.value,
            }
        )
        
        logger.info(
            f"Payment intent created: {payment_intent['payment_intent_id']} "
            f"for user {current_user.id}"
        )
        
        return PaymentIntentResponse(
            success=True,
            payment_id=payment_intent["payment_id"],
            client_secret=payment_intent["client_secret"],
            amount=amount,
            currency="USD",
            subscription_tier=tier.value,
            subscription_months=request_data.subscription_months,
        )
        
    except ValueError as e:
        logger.error(f"Payment intent creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Payment intent creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )


@router.post(
    "/webhook/stripe",
    summary="Stripe webhook",
    description="Handle Stripe webhook events (payment success, failure, refund)"
)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events."""
    
    try:
        # Get raw body
        payload = await request.body()
        
        if not stripe_signature:
            logger.error("Missing Stripe signature header")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )
        
        # Process webhook
        result = await payment_service.handle_stripe_webhook(
            payload=payload,
            signature=stripe_signature
        )
        
        logger.info(f"Webhook processed: {result}")
        
        return {"success": True, "result": result}
        
    except ValueError as e:
        logger.error(f"Webhook validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    except Exception as e:
        logger.exception(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.get(
    "/my-payments",
    response_model=PaymentHistoryResponse,
    summary="Get payment history",
    description="Get current user's payment history"
)
async def get_my_payments(
    current_user: User = Depends(get_current_active_user)
):
    """Get payment history for current user."""
    
    try:
        payments = payment_service.get_payment_logs(
            user_id=str(current_user.id),
            limit=100
        )
        
        # Convert to dict for response
        payments_data = [
            {
                "id": p.id,
                "created_at": p.created_at.isoformat(),
                "provider": p.provider.value,
                "status": p.status.value,
                "amount": p.amount,
                "currency": p.currency,
                "subscription_tier": p.subscription_tier.value,
                "subscription_months": p.subscription_months,
            }
            for p in payments
        ]
        
        return PaymentHistoryResponse(
            success=True,
            payments=payments_data,
            total=len(payments_data)
        )
        
    except Exception as e:
        logger.exception(f"Failed to get payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )


@router.get(
    "/pricing",
    response_model=PricingResponse,
    summary="Get subscription pricing",
    description="Get subscription plans and pricing"
)
async def get_pricing():
    """Get subscription pricing information."""
    
    return PricingResponse(
        success=True,
        pricing=SUBSCRIPTION_PRICING
    )









