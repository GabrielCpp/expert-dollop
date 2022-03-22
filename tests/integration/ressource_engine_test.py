import pytest
from injector import Injector
from uuid import UUID
from datetime import datetime, timezone
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import ProjectDetails, Ressource, User
from expert_dollup.core.utils import encode_date_with_uuid
from expert_dollup.core.utils.ressource_permissions import make_ressource
from expert_dollup.infra.ressource_engine import RessourceEngine, UserRessourceQuery
from expert_dollup.shared.database_services import DbConnection, Page
from ..fixtures import *


@pytest.mark.asyncio
async def test_given_project_it_could_be_paginated_by_user(
    container: Injector, dal: DbConnection, auth_dal: DbConnection
):
    project_service = container.get(CollectionService[ProjectDetails])
    ressource_service = container.get(CollectionService[Ressource])
    user_service = container.get(CollectionService[User])
    mapper = container.get(Mapper)
    projects_by_name = {}

    user_a = UserFactory()
    user_b = UserFactory()

    await dal.truncate_db()
    await auth_dal.truncate_db()

    for i in range(0, 20):
        name = f"project{i}"
        current_user = user_a if i % 2 == 0 else user_b
        project = ProjectDetailsFactory(
            name=name,
            creation_date_utc=datetime(2011, 11, 4, i, 5, tzinfo=timezone.utc),
        )
        await project_service.insert(project)
        await ressource_service.insert(
            make_ressource(ProjectDetails, project, current_user.id)
        )
        projects_by_name[name] = project

    ressource_engine = RessourceEngine(
        user_service, ressource_service, mapper, project_service
    )

    result = await ressource_engine.find_page(UserRessourceQuery(user_a.id), 5, None)
    next_page_token = ressource_engine.make_record_token(projects_by_name["project10"])

    assert result == Page(
        limit=5,
        results=[
            projects_by_name["project18"],
            projects_by_name["project16"],
            projects_by_name["project14"],
            projects_by_name["project12"],
            projects_by_name["project10"],
        ],
        next_page_token=next_page_token,
        total_count=10,
    )

    result = await ressource_engine.find_page(
        UserRessourceQuery(user_a.id), 5, next_page_token
    )
    next_page_token = ressource_engine.make_record_token(projects_by_name["project0"])

    assert result == Page(
        limit=5,
        results=[
            projects_by_name["project8"],
            projects_by_name["project6"],
            projects_by_name["project4"],
            projects_by_name["project2"],
            projects_by_name["project0"],
        ],
        next_page_token=next_page_token,
        total_count=10,
    )

    result = await ressource_engine.find_page(
        UserRessourceQuery(user_a.id), 5, next_page_token
    )

    assert result == Page(
        limit=5,
        results=[],
        next_page_token="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
        total_count=10,
    )
