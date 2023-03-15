from decimal import Decimal
from typing import List, Dict, Protocol, Iterable, Optional
from uuid import UUID
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from .computation import Computation, PrimitiveWithNoneUnion
from .flat_ast_evaluator import FlatAstEvaluator


@dataclass
class UnitRef:
    node_id: UUID
    path: List[UUID]
    name: str


class ValueComputationMethod(Protocol):
    computed: bool

    def update(self, unit: "Unit") -> PrimitiveWithNoneUnion:
        ...


@dataclass
class Unit:
    node_id: UUID
    path: List[UUID]
    name: str
    value: PrimitiveWithNoneUnion = None
    dependencies: List[str] = field(default_factory=list)
    calculation_details: str = ""
    computable: Optional[ValueComputationMethod] = None

    def update_computation(self) -> None:
        if not self.computable is None:
            self.computable.update(self)

    def was_computed(self) -> bool:
        if self.computable is None:
            return True

        return self.computable.computed

    @property
    def report_dict(self) -> dict:
        return asdict(self)


class UnitInjector:
    def __init__(self, *units):
        self.unit_map: Dict[str, List[Unit]] = defaultdict(list)
        self.units: List[Unit] = []
        self.add_all(units)

    def precompute(self) -> None:
        for unit in self.units:
            unit.update_computation()

    def add(self, unit: Unit) -> None:
        for item in unit.path:
            self.unit_map[f"{item}.{unit.name}"].append(unit)

        self.unit_map[unit.name].append(unit)
        self.unit_map[f"{unit.node_id}.{unit.name}"].append(unit)
        self.units.append(unit)

    def add_all(self, units: Iterable[Unit]) -> "UnitInjector":
        for unit in units:
            self.add(unit)

        return self

    def get_by(self, node_id: UUID, path: List[UUID], name: str) -> List[Unit]:
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

    def get_by_name(self, name: str):
        if name in self.unit_map:
            return self.unit_map[name]

        return []

    def get_one_value(self, node_id: UUID, path: List[UUID], name: str, default):
        units = self.get_by(node_id, path, name)

        if len(units) == 0:
            return default

        if len(units) == 1:
            return units[0].value

        # TODO: Fix me
        return f"<Error, {name}>"

    def get_one_value_by_name(self, name: str, default=0):
        units = self.get_by_name(name)

        if len(units) == 0:
            return default

        if len(units) == 1:
            return units[0].value

        raise Exception(f"<Error, {name}>")


class ComputeFlatAst(ValueComputationMethod):
    @staticmethod
    def coerce_decimal(value: PrimitiveWithNoneUnion) -> Decimal:
        if value is None:
            return Decimal(0)

        if isinstance(value, bool):
            return Decimal(int(value))

        if isinstance(value, (int, str)):
            return Decimal(value)

        return value

    def __init__(self, flat_ast: dict, unit_injector: UnitInjector):
        self.flat_ast = flat_ast
        self.unit_injector = unit_injector
        self.evaluator = FlatAstEvaluator()
        self.computed = False

    def update(self, unit: Unit) -> None:
        if self.computed is True:
            return

        lexical_scope = self.build_lexical_scope(unit)
        result, calculation_details = self.evaluator.compute(
            self.flat_ast, lexical_scope
        )
        unit.value = result
        unit.calculation_details = calculation_details
        self.computed = True

    def build_lexical_scope(self, unit: Unit) -> Dict[str, Computation]:
        return {
            dependency: self.build_value(unit, dependency)
            for dependency in unit.dependencies
        }

    def build_value(self, unit: Unit, name: str) -> Computation:
        dependant_units = self.unit_injector.get_by(unit.node_id, unit.path, name)

        for dependant_unit in dependant_units:
            if not dependant_unit.was_computed():
                dependant_unit.update_computation()

        if len(dependant_units) == 1:
            return Computation(
                value=dependant_units[0].value,
                details=f"<{name}[{dependant_units[0].node_id}], {dependant_units[0].value}>",
            )

        sum_result = sum(
            ComputeFlatAst.coerce_decimal(dependant_unit.value)
            for dependant_unit in dependant_units
        )

        return Computation(value=sum_result, details=f"<{sum_result}, sum({name})>")
