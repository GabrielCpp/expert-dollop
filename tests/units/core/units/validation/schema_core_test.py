import pytest
from expert_dollup.shared.database_services import *
from expert_dollup.core.units.validation import *
from tests.fixtures import *


@pytest.mark.asyncio
async def test_validate_project_node(container):
    node = ProjectNodeFactory()
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
            constraints=[
                ConstraintReference("matching-length", "path", "type_path"),
            ],
        )
    )

    validation_context = ValidationContext.from_schema(schema)
    ValidationContext.register_constraint(
        "node-exists",
        lambda: CollectionItemExists(container.get(DatabaseContext), ProjectNode),
    )

    ValidationContext.register_constraint(
        "project-exists",
        lambda: CollectionItemExists(container.get(DatabaseContext), ProjectDetails),
    )

    ValidationContext.register_constraint(
        "definition-node-exists",
        lambda: CollectionItemExists(
            container.get(DatabaseContext), ProjectDefinitionNode
        ),
    )

    results = await validation_context.validate(node)

    print(results)
    assert len(results) == 0
