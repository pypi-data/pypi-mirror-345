from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel

from spryx_iam.types.plan import Periodicity, PlanFeatures


class SubscriptionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    PAST_DUE = "PAST_DUE"


class OrganizationSubscription(BaseModel):
    plan_id: str
    start_date: datetime
    end_date: Optional[datetime]
    status: SubscriptionStatus
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    renewal_date: Optional[datetime]
    price_snapshot: int
    features_snapshot: PlanFeatures
    periodicity_snapshot: Periodicity
    cancellation_date: Optional[datetime]


class Member(BaseModel):
    user_id: str
    name: Optional[str]
    role: str
    image: Optional[str]
    joined_at: datetime


class Organization(BaseModel):
    id: str
    name: str
    subscription: OrganizationSubscription
    members: List[Member]
    created_at: datetime
    updated_at: datetime
