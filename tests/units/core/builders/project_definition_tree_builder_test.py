from ....fixtures import *
from typing import List
from uuid import uuid4
import datetime
from expert_dollup.core.builders.project_definition_tree_builder import (
    ProjectDefinitionTreeBuilder,
)


def generate_node_tree_list(
    roots: list, project_def_id=None, path=None
) -> List[ProjectDefinitionNode]:
    nodes = []
    project_def_id = project_def_id or uuid4()
    path = path or []

    for root in roots:
        new_node = ProjectDefinitionNodeFactory(
            project_def_id=project_def_id, path=path
        )
        nodes.append(new_node)

        if isinstance(root, list):
            children = generate_node_tree_list(
                root, project_def_id, [*path, new_node.id]
            )
            nodes.extend(children)
        else:
            new_node.default_value = root

    return nodes


def test_project_definition_tree_builder_with_unbalenced_tree():

    nodes = [
        ProjectDefinitionNode(
            id=UUID("ab94e29a-33c6-42c1-9296-582769b19153"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_1_form_2",
            is_collection=False,
            instanciate_by_default=True,
            order_index=2,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[
                UUID("df4b4f8c-1e96-4442-a90d-c076acd72163"),
                UUID("d1d3a783-af73-4c3a-842d-e1cc1cf3b2bc"),
            ],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 892675, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("372b51fc-e2f1-4ec5-a97a-17a03c81e9b3"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_0_form_0",
            is_collection=True,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[
                UUID("df4b4f8c-1e96-4442-a90d-c076acd72163"),
                UUID("a844ad25-3d6f-4c5e-a824-8b200e5befc2"),
            ],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 865995, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("40178511-d737-4da9-be83-7da37afa7a3d"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_0_form_2",
            is_collection=False,
            instanciate_by_default=True,
            order_index=2,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[
                UUID("df4b4f8c-1e96-4442-a90d-c076acd72163"),
                UUID("a844ad25-3d6f-4c5e-a824-8b200e5befc2"),
            ],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 876084, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("ca9217a1-44f1-4cf2-96f0-dd76bfadf341"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_1_form_0",
            is_collection=True,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[
                UUID("df4b4f8c-1e96-4442-a90d-c076acd72163"),
                UUID("d1d3a783-af73-4c3a-842d-e1cc1cf3b2bc"),
            ],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 880879, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("3dde424f-8d33-49fc-bc6e-68a9a212556e"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_1_form_1",
            is_collection=False,
            instanciate_by_default=True,
            order_index=1,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[
                UUID("df4b4f8c-1e96-4442-a90d-c076acd72163"),
                UUID("d1d3a783-af73-4c3a-842d-e1cc1cf3b2bc"),
            ],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 885743, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("a5263556-bacf-4f5f-9604-787428ce1b6e"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_0_form_1",
            is_collection=False,
            instanciate_by_default=True,
            order_index=1,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[
                UUID("df4b4f8c-1e96-4442-a90d-c076acd72163"),
                UUID("a844ad25-3d6f-4c5e-a824-8b200e5befc2"),
            ],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 871515, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("25062ca9-64ad-4926-94ed-862c19229142"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="a",
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(
                field_details=CollapsibleContainerFieldConfig(is_collapsible=True),
                value_validator=None,
            ),
            default_value=None,
            path=[UUID("df4b4f8c-1e96-4442-a90d-c076acd72163")],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 19, 4, 57, 98427, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("d1d3a783-af73-4c3a-842d-e1cc1cf3b2bc"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_1",
            is_collection=False,
            instanciate_by_default=True,
            order_index=1,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[UUID("df4b4f8c-1e96-4442-a90d-c076acd72163")],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 880782, tzinfo=datetime.timezone.utc
            ),
        ),
        ProjectDefinitionNode(
            id=UUID("a844ad25-3d6f-4c5e-a824-8b200e5befc2"),
            project_def_id=UUID("80abeca9-bf7a-4d11-a565-94e834485a17"),
            name="root_a_subsection_0",
            is_collection=True,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(field_details=None, value_validator=None),
            default_value=None,
            path=[UUID("df4b4f8c-1e96-4442-a90d-c076acd72163")],
            creation_date_utc=datetime.datetime(
                2021, 4, 17, 18, 59, 19, 865881, tzinfo=datetime.timezone.utc
            ),
        ),
    ]
    builder = ProjectDefinitionTreeBuilder()
    tree = builder.build(nodes)
    flat_tree = [(node.name, trace) for (node, trace) in walk_tree(tree)]

    assert flat_tree == [
        ("a", [0]),
        ("root_a_subsection_0", [1]),
        ("root_a_subsection_0_form_0", [1, 0]),
        ("root_a_subsection_0_form_1", [1, 1]),
        ("root_a_subsection_0_form_2", [1, 2]),
        ("root_a_subsection_1", [2]),
        ("root_a_subsection_1_form_0", [2, 0]),
        ("root_a_subsection_1_form_1", [2, 1]),
        ("root_a_subsection_1_form_2", [2, 2]),
    ]
