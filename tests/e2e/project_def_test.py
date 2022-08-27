import pytest
from dataclasses import dataclass, field
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.utils import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.shared.automapping import Mapper
from ..fixtures import *
from ..utils import find_name


@dataclass
class NodeDefinitionRebinding:
    mapper: Mapper
    static_clock: StaticClock
    db: FakeDb = field(default_factory=lambda: SimpleProject()())
    id_maps: Dict[UUID, UUID] = field(default_factory=dict)

    @property
    def definition(self) -> ProjectDefinition:
        return self.db.get_only_one(ProjectDefinition)

    def rebind_path(
        self,
        definition_node_dto: ProjectDefinitionNodeDto,
    ) -> ProjectDefinitionNodeDto:
        definition_node_dto.path = [self.id_maps[id] for id in definition_node_dto.path]
        return definition_node_dto

    def rebind_values(
        self,
        initial_node_dto: ProjectDefinitionNodeDto,
        new_node_dto: ProjectDefinitionNodeDto,
    ) -> None:
        self.id_maps[initial_node_dto.id] = new_node_dto.id
        initial_node_dto.id = new_node_dto.id
        initial_node_dto.creation_date_utc = self.static_clock.utcnow()

    @property
    def definition_nodes_dto(self) -> List[ProjectDefinitionNode]:
        return self.mapper.map_many(
            self.db.all(ProjectDefinitionNode),
            ProjectDefinitionNodeDto,
            ProjectDefinitionNode,
        )


@pytest.mark.asyncio
async def test_project_creation(ac, mapper, static_clock):
    rebinding = NodeDefinitionRebinding(mapper, static_clock)
    definition_nodes_dto = rebinding.definition_nodes_dto
    await ac.login_super_user()

    definition_dto = await ac.post_json(
        "/api/definitions", rebinding.definition, unwrap_with=ProjectDefinitionDto
    )

    created_node_dtos = [
        await ac.post_json(
            f"/api/definitions/{definition_dto.id}/nodes",
            rebinding.rebind_path(definition_node_dto),
            unwrap_with=ProjectDefinitionNodeDto,
            after=lambda x: rebinding.rebind_values(definition_node_dto, x),
        )
        for definition_node_dto in definition_nodes_dto
    ]

    containers = await AsyncCursor.all(
        ac,
        f"/api/definitions/{definition_dto.id}/nodes",
        after=normalize_request_results(ProjectDefinitionNodeDto, lambda c: c["name"]),
    )

    expected_nodes = normalize_dtos(definition_nodes_dto, lambda c: c["name"])

    assert len(containers) == len(definition_nodes_dto)
    assert containers == expected_nodes


@pytest.mark.asyncio
async def test_query_definition_parts(ac, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()
    definition = db.get_only_one(ProjectDefinition)
    runner = FlowRunner()

    @runner.step
    async def find_all_root_sections():
        root_sections = await ac.get_json(
            f"/api/definitions/{definition.id}/root_sections",
            unwrap_with=ProjectDefinitionNodeTreeDto,
        )
        flat_tree = [(node.name, trace) for (node, trace) in walk_tree(root_sections)]
        expected_flat_tree = [("root_a", [0]), ("root_b", [1])]
        assert flat_tree == expected_flat_tree

        return (root_sections.roots,)

    @runner.step
    async def find_first_root_section_nodes(
        root_sections: List[ProjectDefinitionTreeNode],
    ):
        first_root_section = root_sections[0].definition
        tree = await ac.get_json(
            f"/api/definitions/{definition.id}/root_section_nodes/{first_root_section.id}",
            unwrap_with=ProjectDefinitionNodeTreeDto,
        )
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
        tree = await ac.get_json(
            f"/api/definitions/{definition.id}/form_contents/{form_node.id}",
            unwrap_with=ProjectDefinitionNodeTreeDto,
        )
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
