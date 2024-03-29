import pytest
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_create_get_delete_formula(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(
        SuperUser(), MiniProject(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    project_definition = fake_db.get_only_one(ProjectDefinition)
    formula = FormulaExpressionDtoFactory(
        project_definition_id=project_definition.id,
        attached_to_type_id=fake_db.get_only_one_matching(
            ProjectDefinitionNode, lambda n: n.name == "price"
        ).id,
        name="shipping_price",
        expression="5",
    )
    await ac.post_json(f"/api/definitions/{project_definition.id}/formulas", formula)

    formula = FormulaExpressionDtoFactory(
        project_definition_id=project_definition.id,
        attached_to_type_id=fake_db.get_only_one_matching(
            ProjectDefinitionNode, lambda n: n.name == "root"
        ).id,
        name="article_price",
        expression="shipping_price/sqrt(1)+quantity*price*is_confirmed+4*(item_size == '0')+taxes",
    )
    await ac.post_json(f"/api/definitions/{project_definition.id}/formulas", formula)

    project = ProjectDetailsDtoFactory(project_definition_id=project_definition.id)
    project_dto = await ac.post_json(
        "/api/projects", project, unwrap_with=ProjectDetailsDto
    )

    await ac.post_json(f"/api/projects/{project_dto.id}/formula_cache")

    # response = await ac.get(f"/api/projects/{project.id}formula_cache/{formula.id}")
    # assert response.status_code == 200, response.text
