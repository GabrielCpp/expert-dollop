import expert_dollup.core.usecases as usecases
import expert_dollup.core.units as units
import expert_dollup.core.builders as builders
from expert_dollup.shared.starlette_injection import *


def bind_core_modules(builder: InjectorBuilder) -> None:
    for class_type in [
        *get_classes(builders),
        *get_classes(units),
        *get_classes(usecases),
    ]:
        builder.add_factory(class_type, class_type, **get_annotations(class_type))
