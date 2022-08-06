from typing import List
from dataclasses import dataclass
from expert_dollup.core.domains import User, Organization, OrganizationLimits
from expert_dollup.core.utils.ressource_permissions import all_permisions
from ..factories.helpers import make_uuid


@dataclass
class UserPackage:
    organization: Organization
    users: List[User]


def make_root_user_org(oauth_id: str = "testuser", org_name="root_org") -> UserPackage:
    organization = Organization(
        id=make_uuid(org_name),
        name=org_name,
        limits=OrganizationLimits(
            active_project_count=100,
            active_project_overall_collection_count=1000,
            active_datasheet_count=100,
            active_datasheet_custom_element_count=5000,
        ),
    )

    return UserPackage(
        organization=organization,
        users=[
            User(
                oauth_id=oauth_id,
                id=make_uuid(oauth_id),
                email="testuser@example.com",
                permissions=all_permisions(),
                organization_id=organization.id,
            )
        ],
    )
