import pytest
import factory
from tests.fixtures import *
from expert_dollup.shared.validation.schema_core import *
from expert_dollup.shared.validation.validation_error import ValidationError
from faker.contrib.pytest.plugin import faker


@pytest.mark.asyncio
async def test_validate_project_node(container, faker):
    node = ProjectNodeFactory(path=[faker.uuid4()])
    schema = ValidationSchema(
        root=Object(
            properties={
                "id": String(),
                "project_id": String(
                    constraints=[ConstraintReference("project-exists", "project")]
                ),
                "type_path": Array(
                    items=String(
                        constraints=[
                            ConstraintReference(
                                "definition-node-exists", "definition_node"
                            )
                        ]
                    ),
                    min_items=0,
                    max_items=5,
                    unique_items=True,
                ),
                "type_id": String(
                    constraints=[
                        ConstraintReference("definition-node-exists", "definition_node")
                    ]
                ),
                "type_name": String(),
                "path": Array(
                    items=String(
                        constraints=[ConstraintReference("node-exists", "node")]
                    ),
                    min_items=0,
                    max_items=5,
                    unique_items=True,
                ),
                "label": String(),
            },
            additional_properties=True,
            constraints=[
                ConstraintReference("matching-length", arguments=["path", "type_path"]),
            ],
        )
    )

    validation_context = ValidationContext.from_schema(schema)

    results = await validation_context.validate(node)

    assert results == [
        ErrorMessage(
            kind="matching-length:default",
            message="Validation failed for matching-length:default, expected 2, got 1",
            instance_path="",
            params={"actual": 1, "expected": 2},
        ),
        ErrorMessage(
            kind="project-exists:project",
            message="Validation failed for project-exists:project, expected 1, got 0",
            instance_path="",
            params={"actual": 0, "expected": 1},
        ),
        ErrorMessage(
            kind="definition-node-exists:definition_node",
            message="Validation failed for definition-node-exists:definition_node, expected 3, got 0",
            instance_path="",
            params={"actual": 0, "expected": 3},
        ),
        ErrorMessage(
            kind="node-exists:node",
            message="Validation failed for node-exists:node, expected 1, got 0",
            instance_path="",
            params={"actual": 0, "expected": 1},
        ),
    ]


@pytest.mark.asyncio
async def test_validate_localized_aggregate(container, db_helper):
    localized_aggregate: LocalizedAggregate = LocalizedAggregateFactory()
    await db_helper.load_models(
        ProjectDefinitionFactory(
            id=localized_aggregate.aggregate.project_definition_id
        ),
        AggregateCollectionFactory(id=localized_aggregate.aggregate.collection_id),
    )

    await localized_aggregate.validate()
