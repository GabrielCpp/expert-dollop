import pytest
from base64 import encodebytes
from typing import Union
from injector import Injector
from datetime import datetime, timezone
from expert_dollup.core.domains import ProjectDetails, User
from expert_dollup.core.utils.ressource_permissions import authorization_factory
from expert_dollup.core.repositories import DefinitionNodeFormulaRepository
from expert_dollup.infra.mappings import FIELD_LEVEL
from expert_dollup.shared.database_services import Page
from expert_dollup.shared.database_services import Paginator
from ..fixtures import *


@pytest.mark.asyncio
async def test_formula_node_fetching(container: Injector, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(ProjectInstanceFactory(make_base_project_seed()))
    project_definition = db.get_only_one(ProjectDefinition)
    fields = sorted(
        [
            *db.all_match(ProjectDefinitionNode, lambda n: len(n.path) == FIELD_LEVEL),
            *db.all(Formula),
        ],
        key=lambda x: x.name,
        reverse=True,
    )

    expected_page = Page(
        limit=10,
        results=fields,
        next_page_token=encodebytes(b"fieldA").decode("ascii").strip(),
        total_count=5,
    )
    repository = container.get(DefinitionNodeFormulaRepository)
    paginator = container.get(Paginator[Union[ProjectDefinitionNode, Formula]])

    page = await paginator.find_page(
        repository.make_node_query(project_definition.id, ""), 10
    )

    assert page == expected_page


@pytest.mark.asyncio
async def test_given_formula_node_should_be_fetch_by_name(
    container: Injector, db_helper: DbFixtureHelper
):
    db = await db_helper.load_fixtures(ProjectInstanceFactory(make_base_project_seed()))
    project_definition = db.get_only_one(ProjectDefinition)
    fields = sorted(
        db.all_match(Formula, lambda f: f.name.startswith("formula")),
        key=lambda x: x.name,
        reverse=True,
    )
    limit = 10
    expected_page = Page(
        limit=limit,
        results=fields,
        next_page_token=encodebytes(b"formulaA").decode("ascii").strip(),
        total_count=2,
    )
    repository = container.get(DefinitionNodeFormulaRepository)
    paginator = container.get(Paginator[Union[ProjectDefinitionNode, Formula]])

    page = await paginator.find_page(
        repository.make_node_query(project_definition.id, "formula"), limit
    )

    assert page == expected_page
