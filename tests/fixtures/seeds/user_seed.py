from expert_dollup.core.domains import User
from expert_dollup.core.utils.ressource_permissions import all_permisions
from ..factories.helpers import make_uuid


def make_superuser(oauth_id: str = "testuser"):
    return User(
        oauth_id=oauth_id,
        id=make_uuid(oauth_id),
        email="testuser@example.com",
        permissions=all_permisions(),
    )
