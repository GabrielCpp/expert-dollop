import pytest
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_create_get_delete_formula(ac, expert_dollup_mini_project):
    fake_db = expert_dollup_mini_project
    project_definition = fake_db.project_definitions[0]
    formula = FormulaDtoFactory(
        project_def_id=project_definition.id,
        attached_to_type_id=fake_db.project_definition_nodes[0].id,
        name="shipping_price",
        expression="5",
    )
    response = await ac.post("/api/formula", data=formula.json())
    assert response.status_code == 200, response.text

    formula = FormulaDtoFactory(
        project_def_id=project_definition.id,
        attached_to_type_id=fake_db.project_definition_nodes[0].id,
        name="article_price",
        expression="shipping_price/sqrt(1)+quantity*price*is_confirmed+4*(item_size == '0')+taxes",
    )

    response = await ac.post("/api/formula", data=formula.json())
    assert response.status_code == 200, response.text

    project = ProjectDetailsDtoFactory(project_def_id=project_definition.id)
    response = await ac.post("/api/project", data=project.json())
    assert response.status_code == 200

    project = unwrap(response, ProjectDetailsDto)
    response = await ac.post(f"/api/project/{project.id}/formula_cache")
    assert response.status_code == 200, response.text

    # response = await ac.get(f"/api/project/{project.id}formula_cache/{formula.id}")
    # assert response.status_code == 200, response.text
