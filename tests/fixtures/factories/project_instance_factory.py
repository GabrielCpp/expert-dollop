from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal
from expert_dollup.core.domains import *
from expert_dollup.core.units.evaluator import Unit, ExpressionCompiler
from .domains import *
from .helpers import make_uuid
from ..fake_db_helpers import FakeDb

compiler = ExpressionCompiler.create_simple()


class FormulaSeed:
    def __init__(
        self,
        expression: str,
        formula_dependencies: List[str],
        node_dependencies: List[str],
        calculation_details: str = "",
        result: Decimal = Decimal("0"),
    ):
        self.expression = expression
        self.expression_ast = compiler.compile(expression)
        self.expression_pack = Expression(expression, self.expression_ast)
        self.calculation_details = calculation_details
        self.result = Decimal(result) if isinstance(result, (int, float)) else result
        self.formula_dependencies = formula_dependencies
        self.node_dependencies = node_dependencies
        self._name: Optional[str] = None
        self._def_name: Optional[str] = None
        self._instance_name: Optional[str] = None
        self._node: Optional["NodeSeed"] = None

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    @property
    def def_name(self) -> str:
        assert not self._def_name is None
        return self._def_name

    @property
    def instance_name(self) -> str:
        assert not self._instance_name is None
        return self._instance_name

    @property
    def full_name(self) -> str:
        return f"{self.def_name}-{self.instance_name}-{self.name}"

    @property
    def node(self) -> "NodeSeed":
        assert not self._node is None
        return self._node

    @property
    def id(self):
        return make_uuid(self.name)

    def backfill(
        self,
        name: str,
        instance_name: str,
        formula_name: str,
        project_seed: "ProjectSeed",
    ):
        self._def_name = name
        self._instance_name = instance_name
        self._name = formula_name
        self._node = project_seed.definitions[name].instances[instance_name]


class NodeSeed:
    def __init__(
        self,
        parent: Optional[str] = None,
        value: PrimitiveWithNoneUnion = None,
        formulas: Optional[Dict[str, FormulaSeed]] = None,
    ):
        self.parent = parent
        self.value = value
        self.formulas: Dict[str, FormulaSeed] = formulas or {}
        self._name: Optional[str] = None
        self._def_name: Optional[str] = None
        self._instance_name: Optional[str] = None
        self._path_names: Optional[List[str]] = None
        self._path: Optional[List[UUID]] = None
        self._definition: Optional["DefNodeSeed"] = None

    @property
    def definition(self) -> "DefNodeSeed":
        assert not self._definition is None
        return self._definition

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    @property
    def def_name(self) -> str:
        assert not self._def_name is None
        return self._def_name

    @property
    def instance_name(self) -> str:
        assert not self._instance_name is None
        return self._instance_name

    @property
    def id(self) -> UUID:
        return make_uuid(self.name)

    @property
    def path_names(self) -> List[str]:
        assert not self._path_names is None
        return self._path_names

    @property
    def path(self) -> List[UUID]:
        return [make_uuid(item) for item in self.path_names]

    def backfill(self, name: str, instance_name: str, project_seed: "ProjectSeed"):
        self._def_name = name
        self._instance_name = instance_name
        self._name = f"{name}-{instance_name}"
        self._definition = project_seed.definitions[name]

        for formula_name, formula in self.formulas.items():
            formula.backfill(name, instance_name, formula_name, project_seed)

        self._path_names = (
            []
            if self.parent is None
            else self._build_paths(project_seed, [self.parent])
        )

    def _build_paths(
        self,
        project_seed: "ProjectSeed",
        parents: List[str],
    ) -> List[str]:
        assert len(parents) > 0
        def_name, instance_name = parents[0].split("-")

        assert def_name in project_seed.definitions
        parent_def_seed = project_seed.definitions[def_name]

        assert instance_name in parent_def_seed.instances
        parent_seed = parent_def_seed.instances[instance_name]

        if parent_seed.parent is None:
            return parents

        return self._build_paths(project_seed, [parent_seed.parent, *parents])


class DefNodeSeed:
    def __init__(
        self, instances: Dict[str, NodeSeed] = {}, parent: Optional[str] = None
    ):
        self.instances = instances
        self.parent = parent
        self.is_collection = False
        self.field_details: Optional[FieldDetailsUnion] = None
        self._path_names: Optional[List[str]] = None
        self._translations: Optional[TranslationConfig] = None
        self._name: Optional[str] = None

    @property
    def id(self):
        return make_uuid(self.name)

    @property
    def path_names(self) -> List[str]:
        assert not self._path_names is None
        return self._path_names

    @property
    def path(self) -> List[UUID]:
        return [make_uuid(item) for item in self.path_names]

    @property
    def translations(self) -> TranslationConfig:
        assert not self._translations is None
        return self._translations

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    def backfill(self, name: str, project_seed: "ProjectSeed"):
        self._name = name

        for instance_name, instance in self.instances.items():
            instance.backfill(name, instance_name, project_seed)

        if (
            len(self.instances) > 0
            and len(next(iter(self.instances.values())).path or []) > 0
            and self.parent is None
        ):
            parent_def_name, _ = next(iter(self.instances.values())).parent.split("-")
            self.parent = parent_def_name

        if len(self.instances) > 1:
            self.is_collection = True

        if self._translations is None:
            self._translations = TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            )

        self._path_names = (
            []
            if self.parent is None
            else self._build_paths(project_seed.definitions, [self.parent])
        )

        if len(self.path_names) == 4 and self.field_details is None:
            self.field_details = IntFieldConfig("inch", 0)

    def _build_paths(
        self, definitions: Dict[str, "DefNodeSeed"], parents: List[str], depth: int = 0
    ) -> List[str]:
        assert depth < 6, f"In valid parents references {self._name} -> {parents}"
        assert len(parents) > 0
        assert parents[0] in definitions

        parent_def_seed = definitions[parents[0]]

        if parent_def_seed.parent is None:
            return parents

        return self._build_paths(
            definitions, [parent_def_seed.parent, *parents], depth + 1
        )


@dataclass
class ProjectSeed:
    definitions: Dict[str, DefNodeSeed]

    def __post_init__(self):
        for name, definiton in self.definitions.items():
            definiton.backfill(name, self)

    @property
    def formulas(self) -> List[FormulaSeed]:
        ids = {}

        for definition in self.definitions.values():
            for instance in definition.instances.values():
                for formula in instance.formulas.values():
                    ids[formula.id] = formula

        return list(ids.values())


@dataclass
class CustomProjectInstancePackage:
    project_definition: ProjectDefinition
    project: ProjectDetails
    formulas: List[Formula]
    units: List[Unit]
    definition_nodes: List[ProjectDefinitionNode]
    nodes: List[ProjectNode]
    any_id_to_name: Dict[str, str]


class ProjectInstanceFactory:
    @staticmethod
    def build(
        project_seed: ProjectSeed,
        project_name: str = "test",
        datasheet_id: Optional[UUID] = None,
    ) -> CustomProjectInstancePackage:
        seed_nodes_by_name: Dict[str, NodeSeed] = {}
        units_by_name: Dict[str, FormulaSeed] = {}
        formulas_by_name: Dict[str, FormulaSeed] = {}

        for def_node_seed in project_seed.definitions.values():
            for node_seed in def_node_seed.instances.values():
                node_seed_name = node_seed.name

                assert not node_seed_name in seed_nodes_by_name
                seed_nodes_by_name[node_seed_name] = node_seed

                for formula_seed in node_seed.formulas.values():
                    formula_instance_name = formula_seed.full_name

                    assert not formula_instance_name in units_by_name
                    units_by_name[formula_instance_name] = formula_seed

                    previous_formula_definition = formulas_by_name.get(
                        formula_seed.name, formula_seed
                    )
                    assert (
                        previous_formula_definition.node.definition
                        is formula_seed.node.definition
                    )

                    formulas_by_name[formula_seed.name] = formula_seed

        project_definition = ProjectDefinition(
            id=make_uuid(project_name),
            name=project_name,
            creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000, timezone.utc),
        )

        project = ProjectDetailsFactory(
            id=make_uuid(f"{project_name}-instance"),
            name=project_name,
            is_staged=False,
            project_definition_id=project_definition.id,
            creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000, timezone.utc),
        )

        if not datasheet_id is None:
            project.datasheet_id = datasheet_id

        definition_nodes = [
            ProjectDefinitionNode(
                id=node_def_seed.id,
                project_definition_id=project_definition.id,
                name=node_def_seed.name,
                is_collection=node_def_seed.is_collection,
                instanciate_by_default=True,
                ordinal=index,
                translations=node_def_seed.translations,
                field_details=node_def_seed.field_details,
                path=node_def_seed.path,
                creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000, timezone.utc),
            )
            for index, node_def_seed in enumerate(project_seed.definitions.values())
        ]

        nodes = [
            ProjectNode(
                id=node_seed.id,
                project_id=project.id,
                type_path=node_seed.definition.path,
                type_id=node_seed.definition.id,
                type_name=node_seed.definition.name,
                path=node_seed.path,
                value=node_seed.value,
            )
            for node_seed in seed_nodes_by_name.values()
        ]

        formulas = [
            Formula(
                id=formula_seed.id,
                project_definition_id=project_definition.id,
                attached_to_type_id=formula_seed.node.definition.id,
                expression=formula_seed.expression,
                name=formula_seed.name,
                path=[formula_seed.node.definition.id],
                dependency_graph=FormulaDependencyGraph(
                    formulas=[
                        FormulaDependency(
                            target_type_id=formulas_by_name[dependant_name].id,
                            name=dependant_name,
                        )
                        for dependant_name in formula_seed.formula_dependencies
                    ],
                    nodes=[
                        FormulaDependency(
                            target_type_id=project_seed.definitions[dependant_name].id,
                            name=dependant_name,
                        )
                        for dependant_name in formula_seed.node_dependencies
                    ],
                ),
                creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000, timezone.utc),
            )
            for formula_seed in formulas_by_name.values()
        ]

        units = [
            Unit(
                node_id=formula_instance.node.id,
                path=formula_instance.node.path,
                name=formula_instance.name,
                calculation_details=formula_instance.calculation_details,
                value=formula_instance.result,
            )
            for formula_instance in units_by_name.values()
        ]

        any_id_to_name: Dict[str, str] = {
            project.id: project.name,
            project_definition.id: project_definition.name,
        }

        for seed in project_seed.definitions.values():
            assert not str(seed.id) in any_id_to_name
            any_id_to_name[str(seed.id)] = seed.name

        for seed in seed_nodes_by_name.values():
            assert not str(seed.id) in any_id_to_name
            any_id_to_name[str(seed.id)] = seed.name

        for seed in formulas_by_name.values():
            assert not str(seed.id) in any_id_to_name
            any_id_to_name[str(seed.id)] = seed.name

        return CustomProjectInstancePackage(
            project_definition=project_definition,
            project=project,
            definition_nodes=definition_nodes,
            nodes=nodes,
            formulas=formulas,
            units=units,
            any_id_to_name=any_id_to_name,
        )

    def __init__(self, seed: ProjectSeed):
        self.seed = seed

    def __call__(self, db: FakeDb) -> None:
        package = ProjectInstanceFactory.build(self.seed)
        self.package = package

        db.add(package.project_definition)
        db.add(package.project)
        db.add_all(package.formulas)
        db.add_all(package.definition_nodes)
        db.add_all(package.nodes)
