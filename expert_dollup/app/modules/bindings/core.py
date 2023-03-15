import expert_dollup.core.usecases as usecases
import expert_dollup.core.units as units
import expert_dollup.core.builders as builders
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.core.repositories import *
from expert_dollup.core.units.evaluator import *


def bind_core_modules(builder: InjectorBuilder) -> None:
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
        *get_classes(usecases),
    ]:
        builder.add_factory(class_type, class_type, **get_annotations(class_type))
