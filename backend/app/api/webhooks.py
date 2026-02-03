from fastapi import APIRouter, Request, HTTPException, Header
from sqlalchemy.orm import Session
import stripe
import json

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/stripe")
async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(None)
):
    """Handle Stripe webhook events."""

    payload = await request.body()

    # Check if payload is empty
    if not payload:
        raise HTTPException(
            status_code=400,
            detail="Webhook endpoint - only for Stripe events"
        )

    # Verify webhook signature (in production)
    if settings.STRIPE_WEBHOOK_SECRET and settings.STRIPE_WEBHOOK_SECRET != "whsec_YOUR_WEBHOOK_SECRET_HERE":
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # For development, skip verification
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON payload"
            )

    # Handle event
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    db = SessionLocal()

    try:
        if event_type == "checkout.session.completed":
            # Payment successful, subscription created
            session = data
            subscription_id = session.get("subscription")

            if subscription_id:
                # Retrieve full subscription details
                subscription = stripe.Subscription.retrieve(subscription_id)
                StripeService.update_subscription_from_stripe(subscription, db)

        elif event_type == "customer.subscription.updated":
            # Subscription updated (e.g., plan changed, canceled)
            StripeService.update_subscription_from_stripe(data, db)

        elif event_type == "customer.subscription.deleted":
            # Subscription canceled/ended
            StripeService.update_subscription_from_stripe(data, db)

        elif event_type == "invoice.payment_succeeded":
            # Payment succeeded for renewal
            invoice = data
            subscription_id = invoice.get("subscription")
            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                StripeService.update_subscription_from_stripe(subscription, db)

        elif event_type == "invoice.payment_failed":
            # Payment failed
            invoice = data
            subscription_id = invoice.get("subscription")
            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                StripeService.update_subscription_from_stripe(subscription, db)

    finally:
        db.close()

    return {"status": "success"}