import pytest
from tests.fixtures import *
from .aggregate_service import AggregateService


@pytest.mark.asyncio
async def test_aggregate_insertion(container, faker):
    service = container.get(AggregateService)
    project_definition_id = faker.uuid4()
    collection_id = faker.uuid4()
    new_aggregate = NewAggregateFactory()

    aggregate = await service.create(
        project_definition_id, collection_id, new_aggregate
    )
    print(aggregate)
    assert False
