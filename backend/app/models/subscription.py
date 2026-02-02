from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class SubscriptionStatus(str, enum.Enum):
    """Subscription status from Stripe."""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"

class SubscriptionPlan(str, enum.Enum):
    """Available subscription plans."""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Stripe data
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_price_id = Column(String, nullable=True)

    # Plan and status
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)

    # Timestamps
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(String, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription user_id={self.user_id} plan={self.plan} status={self.status}>"