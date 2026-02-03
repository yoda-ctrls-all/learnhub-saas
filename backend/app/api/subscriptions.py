from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import (
    SubscriptionResponse,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    PlanInfo
)
from app.services.stripe_service import StripeService
from app.api.auth import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/plans", response_model=List[PlanInfo])
def get_plans():
    """Get available subscription plans."""
    return [
        {
            "name": "Free",
            "price_id": "",
            "price": 0.0,
            "currency": "EUR",
            "features": [
                "Access to free courses",
                "Community support",
                "Basic learning materials"
            ]
        },
        {
            "name": "Pro",
            "price_id": settings.STRIPE_PRO_PRICE_ID,
            "price": 9.99,
            "currency": "EUR",
            "features": [
                "Access to all premium courses",
                "Priority support",
                "Downloadable resources",
                "Certificate of completion"
            ]
        },
        {
            "name": "Premium",
            "price_id": settings.STRIPE_PREMIUM_PRICE_ID,
            "price": 19.99,
            "currency": "EUR",
            "features": [
                "Everything in Pro",
                "1-on-1 mentorship sessions",
                "Exclusive workshops",
                "Career guidance",
                "Lifetime access"
            ]
        }
    ]

@router.post("/checkout", response_model=CheckoutSessionResponse)
def create_checkout_session(
        data: CheckoutSessionCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session."""

    # Validate price ID
    valid_prices = [settings.STRIPE_PRO_PRICE_ID, settings.STRIPE_PREMIUM_PRICE_ID]
    if data.price_id not in valid_prices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid price ID"
        )

    # Create checkout session
    try:
        session = StripeService.create_checkout_session(
            user=user,
            price_id=data.price_id,
            success_url="http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/pricing",
            db=db
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )

@router.get("/me", response_model=SubscriptionResponse)
def get_my_subscription(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get current user's subscription."""

    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).order_by(Subscription.created_at.desc()).first()

    if not subscription:
        # Return free plan if no subscription
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    return subscription

@router.post("/portal")
def create_portal_session(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create a Stripe Customer Portal session."""

    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found"
        )

    try:
        portal = StripeService.create_customer_portal_session(
            customer_id=user.stripe_customer_id,
            return_url="http://localhost:3000/dashboard"
        )
        return portal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating portal session: {str(e)}"
        )