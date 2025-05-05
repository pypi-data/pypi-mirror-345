from abc import ABCMeta

from ed_domain.core.entities.user import User
from ed_domain.core.repositories.abc_generic_repository import \
    ABCGenericRepository


class ABCUserRepository(
    ABCGenericRepository[User],
    metaclass=ABCMeta,
):
    ...
