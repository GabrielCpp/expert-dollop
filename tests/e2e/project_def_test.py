import pytest
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from ..fixtures import *
from ..utils import find_name


@pytest.fixture(autouse=True)
async def wip_db(dal):
    await dal.truncate_db()


@pytest.mark.asyncio
async def test_project_creation(ac, mapper):
    db = SimpleProject()()
    project_definition = db.get_only_one(ProjectDefinition)

    response = await ac.post(
        "/api/project_definition", data=jsonify(project_definition)
    )
    assert response.status_code == 200, response.json()

    project_definition_nodes_dto = mapper.map_many(
        db.all(ProjectDefinitionNode),
        ProjectDefinitionNodeDto,
        ProjectDefinitionNode,
    )

    for project_definition_node_dto in project_definition_nodes_dto:
        response = await ac.post(
            "/api/project_definition_node",
            data=project_definition_node_dto.json(),
        )

        assert response.status_code == 200, response.json()

    containers = await AsyncCursor.all(
        ac,
        f"/api/{project_definition.id}/project_definition_nodes",
        after=normalize_request_results(ProjectDefinitionNodeDto, lambda c: c["name"]),
    )

    expected_nodes = normalize_dtos(project_definition_nodes_dto, lambda c: c["name"])

    assert len(containers) == len(project_definition_nodes_dto)
    assert containers == expected_nodes


@pytest.mark.asyncio
async def test_query_project_definition_parts(ac, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(SimpleProject())
    project_definition = db.get_only_one(ProjectDefinition)
    runner = FlowRunner()

    @runner.step
    async def find_all_root_sections():
        response = await ac.get(
            f"/api/project_definition/{project_definition.id}/root_sections"
        )
        assert response.status_code == 200, response.json()

        root_sections = unwrap(response, ProjectDefinitionNodeTreeDto)
        flat_tree = [(node.name, trace) for (node, trace) in walk_tree(root_sections)]
        expected_flat_tree = [("root_a", [0]), ("root_b", [1])]
        assert flat_tree == expected_flat_tree

        return (root_sections.roots,)

    @runner.step
    async def find_first_root_section_nodes(
        root_sections: List[ProjectDefinitionTreeNode],
    ):
        first_root_section = root_sections[0].definition
        response = await ac.get(
            f"/api/project_definition/{project_definition.id}/root_section_nodes/{first_root_section.id}"
        )
        assert response.status_code == 200, response.json()

        tree = unwrap(response, ProjectDefinitionNodeTreeDto)
        flat_tree = [(node.name, trace) for (node, trace) in walk_tree(tree)]
        expected_flat_tree = [
            ("root_a_subsection_0", [0]),
            ("root_a_subsection_0_form_0", [0, 0]),
            ("root_a_subsection_0_form_1", [0, 1]),
            ("root_a_subsection_0_form_2", [0, 2]),
            ("root_a_subsection_1", [1]),
            ("root_a_subsection_1_form_0", [1, 0]),
            ("root_a_subsection_1_form_1", [1, 1]),
            ("root_a_subsection_1_form_2", [1, 2]),
        ]
        assert flat_tree == expected_flat_tree

    @runner.step
    async def find_first_root_section_form_content():
        form_node = find_name(
            db.all(ProjectDefinitionNode), "root_a_subsection_0_form_0"
        )
        response = await ac.get(
            f"/api/project_definition/{project_definition.id}/form_content/{form_node.id}"
        )
        assert response.status_code == 200, response.json()

        tree = unwrap(response, ProjectDefinitionNodeTreeDto)
        flat_tree = [(node.name, trace) for (node, trace) in walk_tree(tree)]
        expected_flat_tree = [
            ("root_a_subsection_0_form_0_section_0", [0]),
            ("root_a_subsection_0_form_0_section_0_field_0", [0, 0]),
            ("root_a_subsection_0_form_0_section_0_field_1", [0, 1]),
            ("root_a_subsection_0_form_0_section_0_field_2", [0, 2]),
            ("root_a_subsection_0_form_0_section_0_field_3", [0, 3]),
            ("root_a_subsection_0_form_0_section_0_field_4", [0, 4]),
            ("root_a_subsection_0_form_0_section_1", [1]),
            ("root_a_subsection_0_form_0_section_1_field_0", [1, 0]),
            ("root_a_subsection_0_form_0_section_1_field_1", [1, 1]),
            ("root_a_subsection_0_form_0_section_1_field_2", [1, 2]),
            ("root_a_subsection_0_form_0_section_1_field_3", [1, 3]),
            ("root_a_subsection_0_form_0_section_1_field_4", [1, 4]),
            ("root_a_subsection_0_form_0_section_2", [2]),
            ("root_a_subsection_0_form_0_section_2_field_0", [2, 0]),
            ("root_a_subsection_0_form_0_section_2_field_1", [2, 1]),
            ("root_a_subsection_0_form_0_section_2_field_2", [2, 2]),
            ("root_a_subsection_0_form_0_section_2_field_3", [2, 3]),
            ("root_a_subsection_0_form_0_section_2_field_4", [2, 4]),
            ("root_a_subsection_0_form_0_section_3", [3]),
            ("root_a_subsection_0_form_0_section_3_field_0", [3, 0]),
            ("root_a_subsection_0_form_0_section_3_field_1", [3, 1]),
            ("root_a_subsection_0_form_0_section_3_field_2", [3, 2]),
            ("root_a_subsection_0_form_0_section_3_field_3", [3, 3]),
            ("root_a_subsection_0_form_0_section_3_field_4", [3, 4]),
        ]
        assert flat_tree == expected_flat_tree

    await runner.run()
