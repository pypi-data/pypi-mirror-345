from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class PeriodicityType(StrEnum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class Periodicity(BaseModel):
    type: PeriodicityType
    interval: int


class PlanFeatures(BaseModel):
    max_ai_messages: Optional[int]
    max_members: Optional[int]
    max_agents: Optional[int]
    max_channels: Optional[int]
    max_storage_bytes: Optional[int]


class Plan(BaseModel):
    pass
