import pytest
from typing import Union
from injector import Injector
from datetime import datetime, timezone
from expert_dollup.core.domains import ProjectDetails, User
from expert_dollup.core.utils.ressource_permissions import authorization_factory
from expert_dollup.infra.mappings import FIELD_LEVEL
from expert_dollup.shared.database_services import Page
from expert_dollup.shared.database_services import Paginator
from ..fixtures import *


@pytest.mark.asyncio
async def test_formula_node_fetching(container: Injector, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(ProjectInstanceFactory(make_base_project_seed()))
    project_definition = db.get_only_one(ProjectDefinition)
    fields = [
        *db.all_match(ProjectNode, lambda n: len(n.path) == FIELD_LEVEL),
        *db.all(Formula),
    ]
    paginator = container.get(Paginator[Union[ProjectDefinitionNode, Formula]])

    page = await paginator.find_page(
        FieldFormulaNodeFilter(project_definition_id=project_definition.id), 10
    )
