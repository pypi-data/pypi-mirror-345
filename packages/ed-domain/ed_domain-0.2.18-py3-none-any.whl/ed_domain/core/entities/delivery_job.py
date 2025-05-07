from datetime import datetime
from enum import StrEnum
from typing import NotRequired
from uuid import UUID

from ed_domain.core.entities.base_entity import BaseEntity


class DeliveryJobStatus(StrEnum):
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DeliveryJob(BaseEntity):
    route_id: UUID
    driver_id: NotRequired[UUID]
    driver_payment_id: NotRequired[UUID]
    status: DeliveryJobStatus
    estimated_payment: float
    estimated_completion_time: datetime
