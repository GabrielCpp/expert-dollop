from uuid import UUID
from dataclasses import dataclass
from typing import Type, Optional, Callable, Any, List, Awaitable, Dict
from pydantic.main import BaseModel
from pydantic.tools import parse_obj_as
from json import loads
from expert_dollup.shared.database_services import DatabaseContext
from expert_dollup.shared.automapping import Mapper
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.usecases import *


class ProjectNodeMetaImport(BaseModel):
    project_id: UUID
    type_id: UUID
    state: ProjectNodeMetaStateDto


class MapProjectNodeMetaImportToDomain:
    def __init__(self, db_context: DatabaseContext):
        self.db_context = db_context
        self.node_by_project_id = {}

    def clear(self):
        self.node_by_project_id = {}

    async def __call__(
        self, models: List[ProjectNodeMetaImport], mapper: Mapper
    ) -> List[ProjectNodeMeta]:
        if len(models) == 0:
            return

        project_id = models[0].project_id

        for model in models:
            assert model.project_id == project_id

        if not project_id in self.node_by_project_id:
            project = await self.db_context.find_by_id(ProjectDetails, project_id)
            definitions = await self.db_context.find_by(
                ProjectDefinitionNode,
                ProjectDefinitionNodeFilter(
                    project_definition_id=project.project_definition_id
                ),
            )

            self.node_by_project_id[project_id] = {
                definition.id: definition for definition in definitions
            }

        defs = self.node_by_project_id[project_id]
        self.clear()

        return [
            ProjectNodeMeta(
                project_id=model.project_id,
                type_id=model.type_id,
                state=ProjectNodeMetaState(**model.state.dict()),
                definition=defs[model.type_id],
            )
            for model in models
        ]


@dataclass
class ImportationMethod:
    dto: BaseModel
    domain: Type
    get_method: Callable[
        [ImportationUseCase], Callable[[User, List[BaseModel]], Awaitable]
    ]
    async_mapper: Optional[Type] = None
    backfill_user_fields: Optional[Callable[[User, dict], dict]] = None

    def load_model(self, user: User, payload: dict) -> BaseModel:
        if not self.backfill_user_fields is None:
            self.backfill_user_fields(user, payload)

        model = parse_obj_as(self.dto, payload)
        return model

    async def map(
        self, models: List[BaseModel], mapper: Mapper, db_context: DatabaseContext
    ):
        if self.async_mapper is None:
            return mapper.map_many(models, self.domain, self.dto)

        map_async = self.async_mapper(db_context)
        return await map_async(models, mapper)

    async def imports(
        self, user: User, domains, importation_use_case: ImportationUseCase
    ):
        method = self.get_method(importation_use_case)
        await method(user, domains)


def fill_original_owner_organization_id(user: User, obj: dict):
    if not "original_owner_organization_id" in obj:
        obj["original_owner_organization_id"] = str(user.organization_id)

    return obj


import_method_by_model_id: Dict[str, ImportationMethod] = {
    "/api/datasheet": ImportationMethod(
        dto=DatasheetImportDto,
        domain=Datasheet,
        get_method=lambda u: u.import_datasheets,
    ),
    "/api/datasheet/element": ImportationMethod(
        dto=DatasheetElementImportDto,
        domain=DatasheetElement,
        get_method=lambda u: u.import_datasheet_elements,
        backfill_user_fields=fill_original_owner_organization_id,
    ),
    "/api/label_collection": ImportationMethod(
        dto=LabelCollectionDto,
        domain=LabelCollection,
        get_method=lambda u: u.import_label_collections,
    ),
    "/api/label": ImportationMethod(
        dto=LabelDto,
        domain=Label,
        get_method=lambda u: u.import_labels,
    ),
    "/api/translation": ImportationMethod(
        dto=TranslationDto,
        domain=Translation,
        get_method=lambda u: u.import_translations,
    ),
    "/api/datasheet_definition_element": ImportationMethod(
        dto=DatasheetDefinitionElementDto,
        domain=DatasheetDefinitionElement,
        get_method=lambda u: u.import_datasheet_definition_elements,
    ),
    "/api/project_definition": ImportationMethod(
        dto=ProjectDefinitionDto,
        domain=ProjectDefinition,
        get_method=lambda u: u.import_project_definitions,
    ),
    "/api/project_definition_node": ImportationMethod(
        dto=ProjectDefinitionNodeDto,
        domain=ProjectDefinitionNode,
        get_method=lambda u: u.import_project_definition_nodes,
    ),
    "/api/formula": ImportationMethod(
        dto=FormulaExpressionDto,
        domain=FormulaExpression,
        get_method=lambda u: u.import_formula_expressions,
    ),
    "/api/unit": ImportationMethod(
        dto=MeasureUnitDto,
        domain=MeasureUnit,
        get_method=lambda u: u.import_measure_units,
    ),
    "/api/report_definition": ImportationMethod(
        dto=ReportDefinitionDto,
        domain=ReportDefinition,
        get_method=lambda u: u.import_report_definition,
    ),
    "raw_project": ImportationMethod(
        dto=ProjectDetailsDto,
        domain=ProjectDetails,
        get_method=lambda u: u.import_projects_details,
    ),
    "raw_node": ImportationMethod(
        dto=ProjectNodeDto,
        domain=ProjectNode,
        get_method=lambda u: u.import_project_nodes,
    ),
    "node_meta": ImportationMethod(
        dto=ProjectNodeMetaImport,
        domain=ProjectNodeMeta,
        get_method=lambda u: u.import_project_node_metas,
        async_mapper=MapProjectNodeMetaImportToDomain,
    ),
}


class ImportRessourceHandler:
    def __init__(
        self,
        importation_usecase: ImportationUseCase,
        db_context: DatabaseContext,
        mapper: Mapper,
    ):
        self.db_context = db_context
        self.importation_usecase = importation_usecase
        self.mapper = mapper

    async def handle(self, user_id: UUID, lines: List[str]):
        models: List[BaseModel] = []
        last_model_id = None
        user = await self.db_context.find_one_by(User, UserFilter(id=user_id))

        for line in lines:
            obj_to_import: dict = loads(line)
            model_id = obj_to_import["type"]
            payload = obj_to_import["payload"]

            if not model_id in import_method_by_model_id:
                raise Exception(f"Ressource type not found: {model_id}")

            loader = import_method_by_model_id[model_id]
            model = loader.load_model(user, payload)

            if last_model_id is None:
                last_model_id = model_id
                models.append(model)
            elif last_model_id == model_id:
                models.append(model)
            else:
                await self.import_models(last_model_id, user, models)
                last_model_id = model_id
                models = [model]

        await self.import_models(last_model_id, user, models)

    async def import_models(self, model_id: str, user: User, models: List[BaseModel]):
        loader = import_method_by_model_id[model_id]
        domains = await loader.map(models, self.mapper, self.db_context)
        await loader.imports(user, domains, self.importation_usecase)
