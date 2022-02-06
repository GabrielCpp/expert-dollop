import pytest
from injector import Injector
from uuid import UUID
from datetime import datetime, timezone
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import ProjectDetails, Ressource, User
from expert_dollup.core.utils.ressource_permissions import make_ressource
from expert_dollup.infra.ressource_engine import RessourceEngine, UserRessourceQuery
from expert_dollup.shared.database_services import DbConnection, Page
from ..fixtures import make_superuser, ProjectDetailsFactory


@pytest.mark.asyncio
async def test_given_project_it_could_be_paginated_by_user(
    container: Injector, dal: DbConnection, auth_dal: DbConnection
):
    project_service = container.get(CollectionService[ProjectDetails])
    ressource_service = container.get(CollectionService[Ressource])
    user_service = container.get(CollectionService[User])
    mapper = container.get(Mapper)
    user_a = make_superuser("user_a")
    user_b = make_superuser("user_b")

    await dal.truncate_db()
    await auth_dal.truncate_db()

    for i in range(0, 20):
        current_user = user_a if i % 2 == 0 else user_b
        project = ProjectDetailsFactory(
            creation_date_utc=datetime(2011, 11, 4, i, 5, tzinfo=timezone.utc)
        )
        await project_service.insert(project)
        await ressource_service.insert(
            make_ressource(ProjectDetails, project, current_user.id)
        )

    ressource_engine = RessourceEngine(
        user_service, ressource_service, mapper, project_service
    )

    result = await ressource_engine.find_page(UserRessourceQuery(user_a.id), 5, None)

    assert result == Page(
        limit=5,
        results=[
            ProjectDetails(
                id=UUID("45e44528-7ba5-8f92-d4be-34a25f116bbb"),
                name="project18",
                is_staged=False,
                project_def_id=UUID("ba35c186-179a-c7b1-7906-347b845729de"),
                datasheet_id=UUID("f5b6d286-7446-05fb-51b2-762e6a506af1"),
                creation_date_utc=datetime(2011, 11, 4, 18, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("eb7e6fa4-cd13-b081-9c0a-a9162a3249da"),
                name="project16",
                is_staged=False,
                project_def_id=UUID("705b99cd-e26d-7177-7cc6-49b09ef540bd"),
                datasheet_id=UUID("afa398d0-92f3-78db-7135-4912601d0210"),
                creation_date_utc=datetime(2011, 11, 4, 16, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("f3450e1f-6ca7-321d-e656-cb67b2a1e154"),
                name="project14",
                is_staged=False,
                project_def_id=UUID("9f12c2c9-c8bf-1f0d-9a48-2bdc03103aab"),
                datasheet_id=UUID("1b2f2ea0-5ab6-443c-adba-8b1278c92258"),
                creation_date_utc=datetime(2011, 11, 4, 14, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("a35fa30f-6c5c-737a-a7ef-bf6dec3f8440"),
                name="project12",
                is_staged=False,
                project_def_id=UUID("cd3025ec-9443-80ec-7c07-d55a7255c06d"),
                datasheet_id=UUID("71627ce3-1c23-f170-09e8-d54aed5cc6f8"),
                creation_date_utc=datetime(2011, 11, 4, 12, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("37887d44-86d1-4d88-f98f-6fbf7a55e41a"),
                name="project10",
                is_staged=False,
                project_def_id=UUID("46affa34-4872-1537-69da-0097278a8c03"),
                datasheet_id=UUID("ab43841b-2239-a781-b024-cb73a80a3b48"),
                creation_date_utc=datetime(2011, 11, 4, 10, 5, tzinfo=timezone.utc),
            ),
        ],
        next_page_token="MjAxMTExMDQxMDA1MDAzNzg4N2Q0NDg2ZDE0ZDg4Zjk4ZjZmYmY3YTU1ZTQxYQ==",
        total_count=10,
    )

    result = await ressource_engine.find_page(
        UserRessourceQuery(user_a.id),
        5,
        "MjAxMTExMDQxMDA1MDAzNzg4N2Q0NDg2ZDE0ZDg4Zjk4ZjZmYmY3YTU1ZTQxYQ==",
    )

    assert result == Page(
        limit=5,
        results=[
            ProjectDetails(
                id=UUID("aaa2e8fe-bc21-41f8-7abb-c9ea50487435"),
                name="project8",
                is_staged=False,
                project_def_id=UUID("d1383682-2265-d0bf-976f-7deb6f28d60c"),
                datasheet_id=UUID("f2cd1be0-6903-9a9d-d9e9-4e4580d1bdc9"),
                creation_date_utc=datetime(2011, 11, 4, 8, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("cad78625-e48e-544e-b9c7-369237caf351"),
                name="project6",
                is_staged=False,
                project_def_id=UUID("1061fea8-3537-c7fe-c577-9ec6e8af3621"),
                datasheet_id=UUID("00fac96c-5400-c41c-842e-90114183d260"),
                creation_date_utc=datetime(2011, 11, 4, 6, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("5ae77aff-7da8-712b-5699-9b5e23c548d6"),
                name="project4",
                is_staged=False,
                project_def_id=UUID("1fcbc512-8382-42e7-cdc5-ae4f63dd3987"),
                datasheet_id=UUID("c06e0078-6594-6898-e5bf-d36c69303094"),
                creation_date_utc=datetime(2011, 11, 4, 4, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("056a4ad6-83cb-f721-2455-68a8baa397f4"),
                name="project2",
                is_staged=False,
                project_def_id=UUID("3a1d2c44-a3c2-728b-93e8-319002d3167d"),
                datasheet_id=UUID("53e5753d-c98f-a36a-1009-aecac22ae386"),
                creation_date_utc=datetime(2011, 11, 4, 2, 5, tzinfo=timezone.utc),
            ),
            ProjectDetails(
                id=UUID("4283fefc-63f0-cd0e-873a-0000c6d07ef7"),
                name="project0",
                is_staged=False,
                project_def_id=UUID("b77e90d3-593a-d699-fc1f-7cd5bb2e35cb"),
                datasheet_id=UUID("f0f19c55-7067-cbbe-80c4-6d1fb6dfbdb0"),
                creation_date_utc=datetime(2011, 11, 4, 0, 5, tzinfo=timezone.utc),
            ),
        ],
        next_page_token="MjAxMTExMDQwMDA1MDA0MjgzZmVmYzYzZjBjZDBlODczYTAwMDBjNmQwN2VmNw==",
        total_count=10,
    )

    result = await ressource_engine.find_page(
        UserRessourceQuery(user_a.id),
        5,
        "MjAxMTExMDQwMDA1MDA0MjgzZmVmYzYzZjBjZDBlODczYTAwMDBjNmQwN2VmNw==",
    )

    assert result == Page(
        limit=5,
        results=[],
        next_page_token="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
        total_count=10,
    )
