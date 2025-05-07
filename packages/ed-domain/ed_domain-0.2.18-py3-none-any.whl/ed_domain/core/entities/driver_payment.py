from datetime import datetime
from enum import StrEnum
from typing import NotRequired, TypedDict

from ed_domain.core.value_objects.money import Money
from ed_domain.core.entities.base_entity import BaseEntity


class DriverPaymentStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentMethod(StrEnum):
    BANK_TRANSFER = "BANK_TRANSFER"
    TELEBIRR = "TELEBIRR"


class DriverPaymentDetail(TypedDict):
    payment_method: PaymentMethod

    # Bank transfer
    account_name: NotRequired[str]
    account_number: NotRequired[str]

    # Telebirr transfer
    phone_number: NotRequired[str]


class DriverPayment(BaseEntity):
    amount: Money
    status: DriverPaymentStatus
    date: datetime
    detail: DriverPaymentDetail
