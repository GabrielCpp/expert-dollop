import ast
from collections import defaultdict
import pytest
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
from expert_dollup.core.units.formula_resolver import FormulaResolver
from expert_dollup.infra.services import (
    FormulaService,
    ProjectNodeService,
    FormulaCacheService,
)
from expert_dollup.core.domains import FormulaNode, FieldNode, FormulaCachedResult

Name = str


@dataclass
class FormulaSeed:
    expression: Optional[str]
    dependencies: List[str]


@dataclass
class NodeSeed:
    parent: Optional[Name] = None
    formulas: Dict[Name, FormulaSeed] = field(default_factory=dict)
    expression: Optional[Dict[str, float]] = None
    instance_parents: Optional[List[str]] = None

    def __post_init__(self):
        if self.instance_parents is None and not self.parent is None:
            self.instance_parents = [f"{self.parent}-0"]


class FormulaFieldFixtureBuilder:
    def __init__(self):
        self.node_graph: Dict[str, NodeSeed] = {}

    def _build_name_id_mapping(self) -> Tuple[Dict[str, UUID], Dict[str, UUID]]:
        name_to_type_id: Dict[str, UUID] = {}
        formula_name_to_type_id: Dict[str, UUID] = {}

        for name, node_seed in self.node_graph.items():
            name_to_type_id[name] = uuid4()

            for formua_name in node_seed.formulas.keys():
                formula_name_to_type_id[formua_name] = uuid4()

        return name_to_type_id, formula_name_to_type_id

    def _build_type_path(
        self, name_to_type_id: Dict[str, UUID]
    ) -> Dict[str, List[UUID]]:
        name_to_type_path: Dict[str, List[UUID]] = {}

        for name in name_to_type_id.keys():
            node_seed = self.node_graph[name]
            path: List[UUID] = []

            while node_seed.parent != None:
                path.append(name_to_type_id[node_seed.parent])
                node_seed = self.node_graph[node_seed.parent]

            path.reverse()
            name_to_type_path[name] = path

        return name_to_type_path

    def _build_instace_mapping(self) -> Dict[str, Tuple[str, UUID]]:
        instance_name_to_id: Dict[str, Tuple[str, UUID]] = {}

        for name, node_seed in self.node_graph.items():
            amount = (
                1
                if node_seed.instance_parents is None
                else len(node_seed.instance_parents)
            )

            for index in range(0, amount):
                instance_name_to_id[f"{name}-{index}"] = (name, uuid4())

        return instance_name_to_id

    def _build_instance_path(
        self,
        instance_name_to_id: Dict[str, Tuple[str, UUID]],
        name_to_type_path: Dict[str, List[UUID]],
    ) -> Dict[str, List[UUID]]:
        instance_name_to_path: Dict[str, List[UUID]] = {}
        name_to_instance_names: Dict[str, List[str]] = defaultdict(list)

        name_to_type_path = sorted(
            list(name_to_type_path.items()), key=lambda x: len(x[1])
        )
        name_to_instance_names = defaultdict(list)

        for instance_name, (name, _) in instance_name_to_id.items():
            name_to_instance_names[name].append(instance_name)

        for name, _ in name_to_type_path:
            node_seed = self.node_graph[name]

            for index, instance_name in enumerate(name_to_instance_names[name]):
                if node_seed.instance_parents is None:
                    instance_name_to_path[instance_name] = []
                    continue

                parent_instance_name = node_seed.instance_parents[index]
                instance_name_to_path[instance_name] = [
                    *instance_name_to_path[parent_instance_name],
                    instance_name_to_id[instance_name][1],
                ]

        return instance_name_to_path

    def get_formula_id(self, formula_name: str) -> UUID:
        return self.formula_name_to_id[formula_name]

    def get_node_instance_id(self, instance_name: str) -> UUID:
        return self.instance_name_to_id[instance_name][1]

    def build(self, node_graph: Dict[str, NodeSeed]):
        self.node_graph = node_graph
        name_to_type_id, formula_name_to_id = self._build_name_id_mapping()
        name_to_type_path = self._build_type_path(name_to_type_id)
        instance_name_to_id = self._build_instace_mapping()
        instance_name_to_path = self._build_instance_path(
            instance_name_to_id, name_to_type_path
        )

        self.name_to_type_id = name_to_type_id
        self.formula_name_to_id = formula_name_to_id
        self.name_to_type_path = name_to_type_path
        self.instance_name_to_id = instance_name_to_id
        self.instance_name_to_path = instance_name_to_path

        formula_nodes = []
        fields = []

        for instance_name, (name, node_id) in instance_name_to_id.items():
            node_seed = node_graph[name]

            for formula_name, formula_seed in node_seed.formulas.items():
                formula_nodes.append(
                    FormulaNode(
                        id=node_id,
                        name=formula_name,
                        path=instance_name_to_path[instance_name],
                        type_id=name_to_type_id[name],
                        type_path=name_to_type_path[name],
                        expression=ast.parse(formula_seed.expression),
                        formula_id=formula_name_to_id[formula_name],
                        dependencies=[
                            name_to_type_id[dep_name]
                            if dep_name in name_to_type_id
                            else formula_name_to_id[dep_name]
                            for dep_name in formula_seed.dependencies
                        ],
                    )
                )

            if node_seed.expression:
                fields.append(
                    FieldNode(
                        id=node_id,
                        name=name,
                        path=instance_name_to_path[instance_name],
                        type_id=name_to_type_id[name],
                        type_path=name_to_type_path[name],
                        expression=node_seed.expression[instance_name],
                    )
                )

        return formula_nodes, fields


@pytest.mark.asyncio
async def test_given_formula_instances_should_compute_collection():
    project_id = uuid4()
    project_definition_id = uuid4()
    formula_service = StrictInterfaceSetup(FormulaService)
    project_node_service = StrictInterfaceSetup(ProjectNodeService)
    project_definition_node_service = StrictInterfaceSetup(ProjectNodeService)
    formula_cache_service = StrictInterfaceSetup(FormulaCacheService)

    node_graphs: Dict[str, NodeSeed] = {
        "rootA": NodeSeed(
            formulas={
                "formulaA": FormulaSeed(
                    expression="fieldB*fieldA", dependencies=["fieldB", "fieldA"]
                )
            }
        ),
        "rootB": NodeSeed(),
        "subSectionA": NodeSeed(parent="rootA"),
        "formA": NodeSeed(parent="subSectionA"),
        "sectionA": NodeSeed(
            parent="formA",
            instance_parents=["formA-0", "formA-0", "formA-0"],
            formulas={
                "sectionA-formula": FormulaSeed(
                    expression="fieldA-2", dependencies=["fieldA"]
                )
            },
        ),
        "fieldA": NodeSeed(
            parent="sectionA",
            expression={"fieldA-0": 5, "fieldA-1": 4, "fieldA-2": 3},
            instance_parents=["sectionA-0", "sectionA-1", "sectionA-2"],
        ),
        "sectionB": NodeSeed(parent="formA"),
        "fieldB": NodeSeed(parent="sectionB", expression={"fieldB-0": 2}),
    }

    tree_fixture = FormulaFieldFixtureBuilder()
    formula_nodes, fields = tree_fixture.build(node_graphs)
    expected_formulas_cache = [
        FormulaCachedResult(
            project_id=project_id,
            formula_id=tree_fixture.get_formula_id("formulaA"),
            node_id=tree_fixture.get_node_instance_id("rootA-0"),
            calculation_details="<fieldB, 2> * sum(<fieldA, 12>)",
            result=24,
        ),
        FormulaCachedResult(
            project_id=project_id,
            formula_id=tree_fixture.get_formula_id("sectionA-formula"),
            node_id=tree_fixture.get_node_instance_id("sectionA-0"),
            calculation_details="<fieldA, 5> - 2",
            result=3,
        ),
        FormulaCachedResult(
            project_id=project_id,
            formula_id=tree_fixture.get_formula_id("sectionA-formula"),
            node_id=tree_fixture.get_node_instance_id("sectionA-1"),
            calculation_details="<fieldA, 4> - 2",
            result=2,
        ),
        FormulaCachedResult(
            project_id=project_id,
            formula_id=tree_fixture.get_formula_id("sectionA-formula"),
            node_id=tree_fixture.get_node_instance_id("sectionA-2"),
            calculation_details="<fieldA, 3> - 2",
            result=1,
        ),
    ]

    formula_service.setup(
        lambda x: x.get_all_project_formula_ast(project_id, project_definition_id),
        returns_async=formula_nodes,
    )

    project_node_service.setup(
        lambda x: x.get_all_fields(project_id), returns_async=fields
    )

    formula_cache_service.setup(
        lambda x: x.repopulate(project_id, expected_formulas_cache), returns_async=None
    )

    formula_resolver = FormulaResolver(
        formula_service.object,
        project_node_service.object,
        project_definition_node_service.object,
        formula_cache_service.object,
    )

    cached_results = await formula_resolver.compute_all_project_formula(
        project_id, project_definition_id
    )
