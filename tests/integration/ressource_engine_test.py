import pytest
from injector import Injector
from datetime import datetime, timezone
from expert_dollup.core.domains import ProjectDetails, User
from expert_dollup.core.utils.ressource_permissions import make_ressource
from expert_dollup.infra.ressource_engine import UserRessourceQuery
from expert_dollup.shared.database_services import Page
from expert_dollup.shared.database_services import UserRessourcePaginator
from ..fixtures import *


def make_projects_with_user():
    db = FakeDb()
    user_a = UserFactory()
    user_b = UserFactory()
    db.add(user_a, user_b)

    for i in range(0, 20):
        name = f"project{i}"
        current_user = user_a if i % 2 == 0 else user_b
        project = ProjectDetailsFactory(
            name=name,
            creation_date_utc=datetime(2011, 11, 4, i, 5, tzinfo=timezone.utc),
        )
        project_ressource = make_ressource(ProjectDetails, project, current_user)
        db.add(project)
        db.add(project_ressource)

    return db


@pytest.mark.asyncio
async def test_given_project_it_could_be_paginated_by_user(
    container: Injector, db_helper: DbFixtureHelper
):
    db = await db_helper.load_fixtures(make_projects_with_user)
    projects = db.all(ProjectDetails)
    user = db.all(User)[0]
    ressource_query = UserRessourceQuery(user.organization_id)
    ressource_engine = container.get(UserRessourcePaginator[ProjectDetails])
    token_page_1 = ressource_engine.make_record_token(projects[10])
    token_page_2 = ressource_engine.make_record_token(projects[0])
    token_page_3 = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
    expected_user_pages = [
        Page(
            limit=5,
            results=[
                projects[18],
                projects[16],
                projects[14],
                projects[12],
                projects[10],
            ],
            next_page_token=token_page_1,
            total_count=10,
        ),
        Page(
            limit=5,
            results=[projects[8], projects[6], projects[4], projects[2], projects[0]],
            next_page_token=token_page_2,
            total_count=10,
        ),
        Page(
            limit=5,
            results=[],
            next_page_token=token_page_3,
            total_count=10,
        ),
    ]

    actual_user_pages = [
        await ressource_engine.find_page(ressource_query, 5, None),
        await ressource_engine.find_page(ressource_query, 5, token_page_1),
        await ressource_engine.find_page(ressource_query, 5, token_page_2),
    ]

    assert actual_user_pages == expected_user_pages
