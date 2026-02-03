from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionPlan, SubscriptionStatus

class SubscriptionBase(BaseModel):
    plan: SubscriptionPlan
    status: SubscriptionStatus

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class CheckoutSessionCreate(BaseModel):
    price_id: str

class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

class PlanInfo(BaseModel):
    name: str
    price_id: str
    price: float
    currency: str
    features: list[str]