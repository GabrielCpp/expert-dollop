from expert_dollup.core.domains import User
from expert_dollup.shared.database_services import CollectionServiceProxy
from ..daos import UserDao


class UserService(CollectionServiceProxy[User]):
    class Meta:
        dao = UserDao
        domain = User
