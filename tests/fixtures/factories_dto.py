import factory
from uuid import uuid4, UUID
from expert_dollup.app.dtos import *


class ProjectDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionDto

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Gab{n}")
    default_datasheet_id = factory.LazyFunction(uuid4)


class ProjectDefinitionContainerDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionContainerDto

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Container{n}")
    is_collection = False
    instanciate_by_default = True
    order_index = factory.Sequence(lambda n: n)
    config = {}
    value_type = "INT"
    default_value = {"value": 0}
    path = []


class TranslationDtoFactory(factory.Factory):
    class Meta:
        model = TranslationDto

    ressource_id = factory.LazyFunction(uuid4)
    locale = "fr"
    name = factory.Sequence(lambda n: f"hello{n}")
    value = factory.Sequence(lambda n: f"translation{n}")


class ProjectDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDto

    id: UUID = factory.LazyFunction(uuid4)
    name: str = factory.Sequence(lambda n: f"project{n}")
    is_staged: bool = False
    project_def_id: UUID = factory.LazyFunction(uuid4)
    datasheet_id: UUID = factory.LazyFunction(uuid4)


class FormulaDtoFactory(factory.Factory):
    class Meta:
        model = FormulaDto

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    attached_to_type_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"formula{n}")
    expression = "a+b*c/2"
    generated_ast = ""
