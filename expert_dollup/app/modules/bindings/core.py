from ast import Call
from typing import Callable
import expert_dollup.core.services as services
import expert_dollup.core.units as units
import expert_dollup.core.builders as builders
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.core.repositories import *
from expert_dollup.core.units.evaluator import *
from expert_dollup.shared.validation import *


def bind_core_modules(builder: InjectorBuilder) -> None:
    bind_validation_constraints(builder)
    builder.add_factory(
        Callable[[ObjectFactory], ObjectFactory], DataclassFactory, injector=Injector
    )

    builder.add_object(FlatAstEvaluator, FlatAstEvaluator(BUILD_INS))
    builder.add_factory(
        units.FormulaResolver,
        to=units.FormulaResolver,
        formula_service=FormulaRepository,
        project_node_service=ProjectNodeRepository,
        project_definition_node_service=ProjectDefinitionNodeRepository,
        stage_formulas_storage=Repository[FormulaPack],
        compiler=InjectorBuilder.forward(ExpressionCompiler.create_simple()),
        logger=LoggerFactory,
    )

    bound_units = set([units.FormulaResolver])
    bindable_units = [unit for unit in get_classes(units) if not unit in bound_units]

    for class_type in [
        *get_classes(builders),
        *bindable_units,
        *get_classes(services),
    ]:
        builder.add_factory(class_type, class_type, **get_annotations(class_type))


def bind_validation_constraints(builder: InjectorBuilder):
    ValidationContext.register_constraint(
        "node-exists",
        builder.add_factory(
            Callable[[DatabaseContext, ProjectNode], CollectionItemExists],
            CollectionItemExists,
            db_context=DatabaseContext,
            domain=InjectorBuilder.forward(ProjectNode),
        ),
    )

    ValidationContext.register_constraint(
        "project-exists",
        builder.add_factory(
            Callable[[DatabaseContext, ProjectNode], CollectionItemExists],
            CollectionItemExists,
            db_context=DatabaseContext,
            domain=InjectorBuilder.forward(ProjectDetails),
        ),
    )

    ValidationContext.register_constraint(
        "project-definition-exists",
        builder.add_factory(
            Callable[[DatabaseContext, ProjectDefinition], CollectionItemExists],
            CollectionItemExists,
            db_context=DatabaseContext,
            domain=InjectorBuilder.forward(ProjectDefinition),
        ),
    )

    ValidationContext.register_constraint(
        "definition-node-exists",
        builder.add_factory(
            Callable[[DatabaseContext, ProjectNode], CollectionItemExists],
            CollectionItemExists,
            db_context=DatabaseContext,
            domain=InjectorBuilder.forward(ProjectDefinitionNode),
        ),
    )

    ValidationContext.register_constraint(
        "collection-exists",
        builder.add_factory(
            Callable[[DatabaseContext, AggregateCollection], CollectionItemExists],
            CollectionItemExists,
            db_context=DatabaseContext,
            domain=InjectorBuilder.forward(AggregateCollection),
        ),
    )

    ValidationContext.register_constraint(
        "matching-length",
        MatchingLength,
    )

    ValidationContext.register_constraint(
        "unique",
        Unique,
    )

    ValidationContext.register_constraint(
        "identical-value",
        IdenticalValue,
    )
