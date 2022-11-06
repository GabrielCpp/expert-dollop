from pydantic.tools import parse_obj_as
import pytest
from collections import defaultdict
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


def assert_all_definition_where_impemented(aggregates, results):
    implementations = defaultdict(int)

    for result in results:
        implementations[result.aggregate_id] += 1

    assert len(aggregates) > 0
    for aggregate in aggregates:
        assert aggregate.id in implementations
        assert implementations.get(aggregate.id) == 1


@pytest.mark.asyncio
async def test_datasheet(ac, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(SuperUser(), MiniDatasheet())
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    collection_element = db.get_by_name(Aggregate, "collection_element")
    single_aggregate = db.get_by_name(Aggregate, "single_element")
    abstract_product = db.get_by_name(AggregateCollection, "abstract_product")

    datasheet_dto = await create_datasheet(
        ac,
        NewDatasheetDtoFactory(
            project_definition_id=definition.id,
            abstract_collection_id=abstract_product.id,
        ),
    )

    elements_page_dto = await get_paginated_datasheet_elements(ac, datasheet_dto)
    assert_all_definition_where_impemented(db.all(Aggregate), elements_page_dto.results)

    # update_single_instance_datasheet_element
    element = next(
        result
        for result in elements_page_dto.results
        if result.aggregate_id == single_aggregate.id
    )

    new_child_element = await replace_datasheet_element(
        ac,
        datasheet_dto.id,
        element.id,
        NewDatasheetElementDtoFactory(
            aggregate_id=single_aggregate.id,
            attributes=[
                AttributeDto(
                    name="lost", value=DecimalFieldValueDto(numeric=Decimal(3))
                ),
                AttributeDto(
                    name="conversion_factor",
                    value=DecimalFieldValueDto(numeric=Decimal(2)),
                ),
            ],
        ),
    )
    datasheet_element_child = await get_datasheet_element(
        ac, datasheet_dto.id, element.id
    )
    assert new_child_element == datasheet_element_child

    # instanciate_collection_element
    element = next(
        result
        for result in elements_page_dto.results
        if result.id == new_child_element.id
    )

    new_child_element = await create_datasheet_element(
        ac,
        datasheet_dto.id,
        NewDatasheetElementDtoFactory(
            aggregate_id=collection_element.id,
            attributes=[
                AttributeDto(name="lost", value=DecimalFieldValueDto(numeric=3.0)),
                AttributeDto(
                    name="conversion_factor",
                    value=DecimalFieldValueDto(numeric=Decimal("1.5")),
                ),
            ],
        ),
    )

    datasheet_element_child = await get_datasheet_element(
        ac, datasheet_dto.id, new_child_element.id
    )
    assert new_child_element == datasheet_element_child

    # delete_collection_element
    await delete_datasheet_element(ac, datasheet_dto.id, new_child_element.id)
    await get_datasheet_element(
        ac, datasheet_dto.id, new_child_element.id, expected_status_code=404
    )


@pytest.mark.asyncio
async def test_datasheet_crud(ac, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(
        SuperUser(), MiniDatasheet(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    abstract_product = db.get_by_name(AggregateCollection, "abstract_product")
    single_aggregate = db.get_by_name(Aggregate, "single_element")

    datasheet_dto = await create_datasheet(
        ac,
        NewDatasheetDtoFactory(
            project_definition_id=definition.id,
            abstract_collection_id=abstract_product.id,
        ),
    )
    cloned_datasheet_dto = await clone_datasheet(ac, datasheet_dto)
    elements_page_dto = await get_paginated_datasheet_element_by_aggregate(
        ac, cloned_datasheet_dto, single_aggregate.id
    )

    updated_datasheet_dto = await patch_datasheet_element_values(
        ac,
        cloned_datasheet_dto.id,
        elements_page_dto.results[0].id,
        [AttributeDto(name="name", value=StringFieldValueDto(text="patched name"))],
    )
    assert updated_datasheet_dto.attributes == [
        AttributeDto(
            name="conversion_factor", value=DecimalFieldValueDto(numeric=Decimal("2"))
        ),
        AttributeDto(name="lost", value=DecimalFieldValueDto(numeric=Decimal("1"))),
        AttributeDto(name="name", value=StringFieldValueDto(text="patched name")),
    ]

    actual_datasheet = await get_datasheet_element(
        ac, cloned_datasheet_dto.id, elements_page_dto.results[0].id
    )
    assert actual_datasheet == updated_datasheet_dto

    await delete_datasheet(ac, datasheet_dto.id)
