from ed_domain.core.entities.user import User
from ed_domain.core.repositories.abc_user_repository import ABCUserRepository

from ed_infrastructure.persistence.mongo_db.db_client import DbClient
from ed_infrastructure.persistence.mongo_db.repositories.generic_repository import \
    GenericRepository


class UserRepository(GenericRepository[User], ABCUserRepository):
    def __init__(self, db_client: DbClient) -> None:
        super().__init__(db_client, "user")
