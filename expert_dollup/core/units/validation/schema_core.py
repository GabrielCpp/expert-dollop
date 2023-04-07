from dataclasses import dataclass, field
from typing import Protocol, Optional, Callable, Any, List, Dict
from decimal import Decimal

AddBoundError = Callable[[Any, Any], None]


class SchemaError(Exception):
    def __init__(self, type, message, instancePath: str, **kawgs):
        Exception.__init__(self, message)
        self.type = type
        self.instancePath = instancePath
        self.details = kawgs


@dataclass
class ConstraintAddContext:
    validation_context: "ValidationContext"
    reference: "ConstraintReference"
    errors: List["ErrorMessage"]

    @property
    def instance_path(self) -> List[str]:
        return self.validation_context.instance_path

    @property
    def arguments(self) -> List[str]:
        return self.reference.arguments

    def add_error(self, actual: Any, expected) -> None:
        self.validation_context.add_error(
            self.errors,
            f"{self.reference.kind}:{self.reference.name}",
            actual,
            expected,
        )


@dataclass
class ConstraintValidationContext:
    validation_context: "ValidationContext"
    kind: str
    name: str

    @property
    def instance_path(self) -> List[str]:
        return self.validation_context.instance_path

    def add_error(self, actual: Any, expected) -> None:
        self.validation_context.add_error(
            self.validation_context.schema.errors,
            f"{self.kind}:{self.name}",
            actual,
            expected,
        )


class Constraint(Protocol):
    def add(self, context: ConstraintAddContext, value: Any) -> None:
        ...

    async def validate(self, context: ConstraintValidationContext) -> None:
        ...


class Schema(Protocol):
    type: str

    def validate(self, context: "ValidationContext", target: Any) -> None:
        ...


@dataclass
class ErrorMessage:
    keyword: str
    message: str


class ValidationContext:
    _CONSTRAINT_FACTORIES: Dict[str, Callable[[str], Constraint]] = {}

    @staticmethod
    def register_constraint(kind: str, f):
        ValidationContext._CONSTRAINT_FACTORIES[kind] = f

    @staticmethod
    def get_object(obj, name):
        if hasattr(obj, name):
            return getattr(obj, name), True

        return None, False

    @staticmethod
    def from_schema(schema: "ValidationSchema") -> "ValidationContext":
        return ValidationContext(schema, ValidationContext.get_object)

    def __init__(
        self,
        schema: "ValidationSchema",
        access: Callable[[Any], Any],
    ):
        self.schema = schema
        self.access = access
        self.errors: List[SchemaError] = []
        self.instance_path: List[str] = []
        self.constraints: Dict[str, Dict[str, Constraint]] = {}

    def validate_child(self, schema: Schema, name: str, target: Any) -> None:
        self.instance_path.append(name)

        try:
            schema.validate(self, target)
        finally:
            self.instance_path.pop()

    def validate_constraint(
        self, errors: List[ErrorMessage], reference: "ConstraintReference", target: Any
    ) -> None:
        instances = self.constraints.get(reference.kind, None)

        if instances is None:
            create_constraint = ValidationContext._CONSTRAINT_FACTORIES.get(
                reference.kind, None
            )

            if create_constraint is None:
                raise Exception(f"No such constraint kind {reference.kind}")

            instances = {reference.name: create_constraint()}
            self.constraints[reference.kind] = instances

        constraint = instances.get(reference.name, None)

        if constraint is None:
            constraint = ValidationContext._CONSTRAINT_FACTORIES[reference.kind]()
            instances[reference.name] = constraint

        constraint.add(ConstraintAddContext(self, reference, errors), target)

    def add_error(
        self, errors: List[ErrorMessage], keyword: str, actual: Any, expected: Any
    ) -> None:
        matching_errors = [error for error in errors if error.keyword == keyword]

        for error in matching_errors:
            self.errors.append(
                SchemaError(
                    keyword,
                    error.message,
                    self.instance_path,
                    actual=actual,
                    expected=expected,
                )
            )
        else:
            self.errors.append(
                SchemaError(
                    keyword,
                    f"Validation failed for {keyword}, expected {expected}, got {actual}",
                    self.instance_path,
                    actual=actual,
                    expected=expected,
                )
            )

    async def validate(self, target: Any) -> List[SchemaError]:
        self.schema.root.validate(self, target)

        for kind, instances in self.constraints.items():
            for name, constraint in instances.items():
                await constraint.validate(ConstraintValidationContext(self, kind, name))

        return self.errors


@dataclass
class ValidationSchema:
    root: "Schema"
    definitions: Dict[str, "Schema"] = field(default_factory=dict)
    errors: List[SchemaError] = field(default_factory=list)


@dataclass
class ConstraintReference:
    kind: str
    name: str = "default"
    arguments: List[str] = field(default_factory=list)


@dataclass
class Integer:
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    exclusive_minimum: Optional[int] = None
    exclusive_maximum: Optional[int] = None
    multiple_of: Optional[int] = None
    constraints: List[ConstraintReference] = field(default_factory=list)
    errors: List[ErrorMessage] = field(default_factory=list)

    @property
    def type(self):
        return "integer"

    def validate(self, context: ValidationContext, target: Any) -> None:
        value = target if isinstance(target, int) else int(target)

        if not self.minimum is None and not (target >= self.minimum):
            context.add_error(self.errors, "minimum", value, self.minimum)

        if not self.maximum is None and not (target <= self.maximum):
            context.add_error(self.errors, "maximum", value, self.maximum)

        if not self.exclusive_minimum is None and not (target < self.exclusive_minimum):
            context.add_error(
                self.errors, "exclusive_minimum", value, self.exclusive_minimum
            )

        if not self.exclusive_maximum is None and not (target < self.exclusive_maximum):
            context.add_error(
                self.errors, "exclusive_maximum", value, self.exclusive_maximum
            )

        if not self.multiple_of is None and target % self.multiple_of != 0:
            context.add_error(self.errors, "multiple_of", value, self.multiple_of)


@dataclass
class Number:
    minimum: Optional[Decimal] = None
    maximum: Optional[Decimal] = None
    exclusive_minimum: Optional[Decimal] = None
    exclusive_maximum: Optional[Decimal] = None
    multiple_of: Optional[Decimal] = None
    constraints: List[ConstraintReference] = field(default_factory=list)
    errors: List[ErrorMessage] = field(default_factory=list)

    @property
    def type(self):
        return "number"

    def validate(self, context: ValidationContext, target: Any) -> None:
        value = target if isinstance(target, Decimal) else Decimal(target)

        if not self.minimum is None and not (target >= self.minimum):
            context.add_error(self.errors, "minimum", value, self.minimum)

        if not self.maximum is None and not (target <= self.maximum):
            context.add_error(self.errors, "maximum", value, self.maximum)

        if not self.exclusive_minimum is None and not (target < self.exclusive_minimum):
            context.add_error(
                self.errors, "exclusive_minimum", value, self.exclusive_minimum
            )

        if not self.exclusive_maximum is None and not (target < self.exclusive_maximum):
            context.add_error(
                self.errors, "exclusive_maximum", value, self.exclusive_maximum
            )

        if (
            not self.multiple_of is None
            and (target / self.multiple_of).as_integer_ratio()[1] != 1
        ):
            context.add_error(self.errors, "multiple_of", value, self.multiple_of)


@dataclass
class String:
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum: Optional[List[str]] = None
    constraints: List[ConstraintReference] = field(default_factory=list)
    errors: List[ErrorMessage] = field(default_factory=list)

    @property
    def type(self):
        return "string"

    def validate(self, context: ValidationContext, target: Any) -> None:
        value = target if isinstance(target, str) else str(target)

        if not self.min_length is None and not (len(value) >= self.min_length):
            context.add_error(self.errors, "min_length", value, self.min_length)

        if not self.max_length is None and not (len(value) >= self.max_length):
            context.add_error(self.errors, "max_length", value, self.max_length)

        if not self.enum is None and not value in self.enum:
            context.add_error(self.errors, "enum", value, enum)

        for constraint in self.constraints:
            context.validate_constraint(self.errors, constraint, value)


@dataclass
class Array:
    items: Schema
    min_items: Optional[int]
    max_items: Optional[int]
    unique_items: bool = False
    constraints: List[ConstraintReference] = field(default_factory=list)
    errors: List[ErrorMessage] = field(default_factory=list)

    @property
    def type(self):
        return "array"

    def validate(self, context: ValidationContext, target: Any) -> None:
        value = target if isinstance(target, list) else list(target)

        if not self.min_items is None and not (len(value) >= self.min_items):
            context.add_error(self.errors, "min_items", value, self.min_items)

        if not self.max_items is None and not (len(value) <= self.max_items):
            context.add_error(self.errors, "max_items", value, self.max_items)

        if self.unique_items:
            items = Array.find_repeated_items(value)
            if len(items) > 0:
                context.add_error(self.errors, "unique_items", value, items)

        for constraint in self.constraints:
            context.validate_constraint(self.errors, constraint, value)

        for index, element in enumerate(value):
            context.validate_child(self.items, str(index), element)

    @staticmethod
    def find_repeated_items(elements: list) -> list:
        seen = set()
        repeated = []

        for element in elements:
            if element in seen:
                repeated.append(element)

            seen.add(element)

        return repeated


@dataclass
class Object:
    properties: Dict[str, Schema]
    patternProperties: Dict[str, Schema] = field(default_factory=dict)
    additionalProperties: bool = False
    required: List[str] = field(default_factory=list)
    constraints: List[ConstraintReference] = field(default_factory=list)
    errors: List[ErrorMessage] = field(default_factory=list)

    @property
    def type(self):
        return "object"

    def validate(self, context: ValidationContext, target: Any) -> None:
        for name, schema in self.properties.items():
            value, ok = context.access(target, name)

            if ok:
                context.validate_child(schema, name, value)
            else:
                context.add_error("properties", value, "name")
