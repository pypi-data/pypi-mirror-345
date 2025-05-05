from typing import NotRequired

from ed_domain.core.entities.base_entity import BaseEntity


class User(BaseEntity):
    first_name: str
    last_name: str
    email: NotRequired[str]
    phone_number: NotRequired[str]
    password: str
    verified: bool
