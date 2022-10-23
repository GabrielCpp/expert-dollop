from typing import Optional
from expert_dollup.core.domains import *
from expert_dollup.core.utils import authorization_factory
from ..fake_db_helpers import FakeDb
from .domains import *
from .super_user import SuperUser


class GrantRessourcePermissions:
    def __init__(self, oauth_id: Optional[str] = SuperUser.oauth_id):
        self.oauth_id = oauth_id

    def __call__(self, db: FakeDb) -> None:
        user = db.get_only_one_matching(User, lambda u: u.oauth_id == self.oauth_id)

        for ressource_type in authorization_factory.ressource_types:
            db.add_all(
                [
                    authorization_factory.allow_access_to(instance, user)
                    for instance in db.all(ressource_type)
                ]
            )
