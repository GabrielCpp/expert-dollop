from uuid import UUID
from typing import List
from expert_dollup.core.domains import *
from expert_dollup.core.utils import authorization_factory
from ..fake_db_helpers import FakeDb
from ..factories import FieldConfigFactory
from ..factories_domain import *
from ..factories.helpers import make_uuid


class SuperUser:
    oauth_id: str = "testuser"

    def __call__(self, db: FakeDb) -> None:
        oauth_id: str = SuperUser.oauth_id
        org_name = "root_org"
        email = f"{oauth_id}@example.com"
        organization = Organization(
            id=make_uuid(org_name),
            name=org_name,
            email=email,
            limits=OrganizationLimits(
                active_project_count=100,
                active_project_overall_collection_count=1000,
                active_datasheet_count=100,
                active_datasheet_custom_element_count=5000,
            ),
        )
        db.add(organization)

        user = User(
            oauth_id=oauth_id,
            id=make_uuid(oauth_id),
            email=email,
            permissions=authorization_factory.build_super_user_permisions(),
            organization_id=organization.id,
        )
        db.add(user)
