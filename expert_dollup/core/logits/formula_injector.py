from decimal import Decimal
from typing import List, Dict, Protocol
from uuid import UUID
from collections import defaultdict
from functools import cached_property
from expert_dollup.core.domains.project_node import ProjectNode
from expert_dollup.core.domains import UnitInstance, PrimitiveUnion, ProjectNode
import expert_dollup.core.logits.formula_processor as formula_processor


class UnitLike(Protocol):
    name: str
    path: List[UUID]
    node_id: UUID


class FormulaInjector:
    def __init__(self):
        self.unit_map: Dict[str, List[UnitLike]] = defaultdict(list)
        self.units: List[UnitLike] = []

    def add_unit(self, unit: UnitLike) -> None:
        for item in unit.path:
            self.unit_map[f"{item}.{unit.name}"].append(unit)

        self.unit_map[unit.name].append(unit)
        self.unit_map[f"{unit.node_id}.{unit.name}"].append(unit)
        self.units.append(unit)

    def get_unit(self, node_id: UUID, path: List[UUID], name: str) -> List[UnitLike]:
        unit_id = f"{node_id}.{name}"

        if unit_id in self.unit_map:
            return self.unit_map[unit_id]

        for id in reversed(path):
            unit_id = f"{id}.{name}"

            if unit_id in self.unit_map:
                return self.unit_map[unit_id]

        if name in self.unit_map:
            return self.unit_map[name]

        return []

    def get_one_value(self, node_id: UUID, path: List[UUID], name: str, default):
        units = self.get_unit(node_id, path, name.lower())

        if len(units) == 0:
            return default

        if len(units) == 1:
            return units[0].value

        # TODO: Fix me
        return "<Error>"
        raise Exception(f"Too many value for {name} in node {node_id}")


class FrozenUnit:
    def __init__(self, formula_instance: UnitInstance):
        self._formula_instance = formula_instance

    @property
    def node_id(self) -> UUID:
        return self._formula_instance.node_id

    @property
    def path(self) -> List[UUID]:
        return self._formula_instance.path

    @property
    def name(self) -> str:
        return self._formula_instance.name

    @property
    def value(self) -> PrimitiveUnion:
        return self._formula_instance.result


class FormulaUnit:
    def __init__(
        self,
        formula_instance: UnitInstance,
        formula_dependencies: List[str],
        final_ast: dict,
        formula_injector: FormulaInjector,
    ):
        self._formula_instance = formula_instance
        self._formula_dependencies = formula_dependencies
        self._final_ast = final_ast
        self._formula_injector = formula_injector
        self._touched = None

    @property
    def dependencies(self) -> List[str]:
        return self._formula_dependencies

    @property
    def node_id(self) -> UUID:
        return self._formula_instance.node_id

    @property
    def path(self) -> List[UUID]:
        return self._formula_instance.path

    @property
    def name(self) -> str:
        return self._formula_instance.name

    @property
    def formula_id(self) -> UUID:
        return self._formula_instance.formula_id

    @cached_property
    def computed(self) -> UnitInstance:
        self.units = {
            name: self._formula_injector.get_unit(self.node_id, self.path, name)
            for name in self.dependencies
        }

        result, calculation_details = formula_processor.compute(self._final_ast, self)

        if result != self._formula_instance.result:
            self._formula_instance.result = result
            self._touched = True

        if self._formula_instance.calculation_details != calculation_details:
            self._formula_instance.calculation_details = calculation_details
            self._touched = True

        return self._formula_instance

    @property
    def touched(self) -> bool:
        if self._touched is None:
            self.computed

        return self._touched

    @property
    def value(self) -> PrimitiveUnion:
        return self.computed.result


class FieldUnit:
    def __init__(self, node: ProjectNode):
        self._node = node
        self._value = self._node.value

        if isinstance(self._value, int):
            self._value = Decimal(self._value)

    @property
    def value(self) -> PrimitiveUnion:
        return self._value

    @property
    def node_id(self) -> UUID:
        return self._node.id

    @property
    def path(self) -> List[UUID]:
        return self._node.path

    @property
    def name(self) -> str:
        return self._node.type_name

    @property
    def computed(self) -> UnitInstance:
        return UnitInstance(
            calculation_details="",
            formula_id=None,
            name=self.name,
            node_id=self.node_id,
            path=self.path,
            result=self.value,
        )