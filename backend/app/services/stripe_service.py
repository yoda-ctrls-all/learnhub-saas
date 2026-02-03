import stripe
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus

logger = logging.getLogger(__name__)


class StripeService:
    """Service for handling Stripe operations."""

    _configured = False

    @classmethod
    def _ensure_configured(cls):
        """
        Ensure Stripe is configured with the API key.
        Uses class variable to configure only once.
        """
        if not cls._configured:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            cls._configured = True

    @staticmethod
    def create_customer(user: User, db: Session) -> str:
        """Create a Stripe customer for a user."""
        StripeService._ensure_configured()

        if user.stripe_customer_id:
            return user.stripe_customer_id

        customer = stripe.Customer.create(
            email=user.email,
            name=user.username,
            metadata={
                "user_id": user.id,
                "username": user.username
            }
        )

        user.stripe_customer_id = customer.id
        db.commit()

        return customer.id

    @staticmethod
    def create_checkout_session(
            user: User,
            price_id: str,
            success_url: str,
            cancel_url: str,
            db: Session
    ) -> Dict[str, Any]:
        """Create a Stripe Checkout session."""
        StripeService._ensure_configured()

        customer_id = StripeService.create_customer(user, db)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id
            }
        )

        return {
            "session_id": session.id,
            "url": session.url
        }

    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from Stripe."""
        StripeService._ensure_configured()

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError:
            return None

    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a subscription."""
        StripeService._ensure_configured()

        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
        except stripe.error.StripeError:
            return False

    @staticmethod
    def create_customer_portal_session(customer_id: str, return_url: str) -> Dict[str, Any]:
        """Create a Stripe Customer Portal session."""
        StripeService._ensure_configured()

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return {
            "url": session.url
        }

    @staticmethod
    def update_subscription_from_stripe(
            subscription_data: Dict[str, Any],
            db: Session
    ) -> Optional[Subscription]:
        """Update local subscription from Stripe webhook data."""
        StripeService._ensure_configured()

        stripe_sub_id = subscription_data.get("id")
        customer_id = subscription_data.get("customer")
        status = subscription_data.get("status")

        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            return None

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()

        if not subscription:
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id=stripe_sub_id
            )
            db.add(subscription)

        subscription.status = SubscriptionStatus(status)
        subscription.stripe_price_id = subscription_data["items"]["data"][0]["price"]["id"]

        if subscription.stripe_price_id == settings.STRIPE_PRO_PRICE_ID:
            subscription.plan = SubscriptionPlan.PRO
        elif subscription.stripe_price_id == settings.STRIPE_PREMIUM_PRICE_ID:
            subscription.plan = SubscriptionPlan.PREMIUM

        subscription.current_period_start = subscription_data.get("current_period_start")
        subscription.current_period_end = subscription_data.get("current_period_end")
        subscription.cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)

        db.commit()
        db.refresh(subscription)

        return subscription