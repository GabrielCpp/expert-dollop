from uuid import uuid4
from expert_dollup.core.domains import *
from expert_dollup.core.utils.ressource_permissions import actions, Action
from expert_dollup.shared.database_services import DatabaseContext
from expert_dollup.core.utils import make_permissions, all_action


class OrganizationUseCase:
    def __init__(self, db_context: DatabaseContext):
        self.db_context = db_context

    async def setup_organization(
        self, email: str, organization_name: str, oauth_id
    ) -> User:
        organization = Organization(
            id=uuid4(),
            name=organization_name,
            limits=OrganizationLimits(
                active_project_count=100,
                active_project_overall_collection_count=1000,
                active_datasheet_count=100,
                active_datasheet_custom_element_count=5000,
            ),
        )

        user = User(
            oauth_id=oauth_id,
            id=uuid4(),
            email=email,
            permissions=[
                *make_permissions(ProjectDetails, all_action()),
                *make_permissions(Datasheet, all_action()),
                *make_permissions(ProjectDefinition, actions(Action.CAN_READ)),
            ],
            organization_id=organization.id,
        )

        await self.db_context.insert(Organization, organization)
        await self.db_context.insert(User, user)
        return user
