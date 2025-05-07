from ed_domain.core.value_objects.money import Money
from ed_domain.core.entities.base_entity import BaseEntity


class Bill(BaseEntity):
    amount: Money
    paid: bool
