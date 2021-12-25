from fastapi import APIRouter, Depends, File, UploadFile
from uuid import UUID
from dataclasses import dataclass
from typing import Type, Optional, Callable, Any, List
from pydantic.main import BaseModel
from pydantic.tools import parse_obj_as
from injector import Injector
from json import loads
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.automapping import Mapper
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.usecases import *
from expert_dollup.infra.services import *

router = APIRouter()


@dataclass
class RessourceLoader:
    dto: Type
    domain: Type
    usecase: Type
    method: str = "add"
    perform_complex_mapping: Optional[Callable[[Injector, BaseModel], Any]] = None

    async def do_mapping(
        self, injector: Injector, mapper: Mapper, ressource_spec: List[BaseModel]
    ) -> Any:
        if self.perform_complex_mapping is None:
            return mapper.map_many(ressource_spec, self.domain, self.dto)

        return await self.perform_complex_mapping(injector, ressource_spec)


class ProjectNodeMetaImport(BaseModel):
    project_id: UUID
    type_id: UUID
    state: ProjectNodeMetaStateDto


class MapProjectNodeMetaImportToDomain:
    def __init__(self):
        self.node_by_project_id = {}

    def clear(self):
        self.node_by_project_id = {}

    async def __call__(
        self, injector: Injector, models: List[ProjectNodeMetaImport]
    ) -> List[ProjectNodeMeta]:
        if len(models) == 0:
            return

        project_definition_node_service = injector.get(ProjectDefinitionNodeService)
        project_id = models[0].project_id

        for model in models:
            assert model.project_id == project_id

        if not project_id in self.node_by_project_id:
            project_service = injector.get(ProjectService)
            project = await project_service.find_by_id(project_id)
            definitions = await project_definition_node_service.find_by(
                ProjectDefinitionNodeFilter(project_def_id=project.project_def_id)
            )

            self.node_by_project_id[project_id] = {
                definition.id: definition for definition in definitions
            }

        return [
            ProjectNodeMeta(
                project_id=model.project_id,
                type_id=model.type_id,
                state=ProjectNodeMetaState(**model.state.dict()),
                definition=self.node_by_project_id[project_id][model.type_id],
            )
            for model in models
        ]


ressources = {
    "/api/datasheet_definition": RessourceLoader(
        dto=DatasheetDefinitionDto,
        domain=DatasheetDefinition,
        usecase=DatasheetDefinitionUseCase,
    ),
    "/api/datasheet": RessourceLoader(
        dto=DatasheetImportDto,
        domain=Datasheet,
        usecase=DatasheetUseCase,
    ),
    "/api/datasheet/element": RessourceLoader(
        dto=DatasheetElementImportDto,
        domain=DatasheetElement,
        usecase=DatasheetElementUseCase,
        method="import_element",
    ),
    "/api/label_collection": RessourceLoader(
        dto=LabelCollectionDto,
        domain=LabelCollection,
        usecase=LabelCollectionService,
        method="insert_many",
    ),
    "/api/label": RessourceLoader(
        dto=LabelDto,
        domain=Label,
        usecase=LabelService,
        method="insert_many",
    ),
    "/api/translation": RessourceLoader(
        dto=TranslationDto,
        domain=Translation,
        usecase=TranslationService,
        method="insert_many",
    ),
    "/api/datasheet_definition_element": RessourceLoader(
        dto=DatasheetDefinitionElementDto,
        domain=DatasheetDefinitionElement,
        usecase=DatasheetDefinitionElementUseCase,
    ),
    "/api/project_definition": RessourceLoader(
        dto=ProjectDefinitionDto,
        domain=ProjectDefinition,
        usecase=ProjectDefinitonUseCase,
    ),
    "/api/project_definition_node": RessourceLoader(
        dto=ProjectDefinitionNodeDto,
        domain=ProjectDefinitionNode,
        usecase=ProjectDefinitionNodeUseCase,
    ),
    "/api/formula": RessourceLoader(
        dto=FormulaExpressionDto,
        domain=FormulaExpression,
        usecase=FormulaUseCase,
    ),
    "/api/unit": RessourceLoader(
        dto=MeasureUnitDto,
        domain=MeasureUnit,
        usecase=MeasureUnitService,
        method="insert_many",
    ),
    "/api/report_definition": RessourceLoader(
        dto=ReportDefinitionDto,
        domain=ReportDefinition,
        usecase=ReportDefinitionUseCase,
    ),
    "raw_project": RessourceLoader(
        dto=ProjectDetailsDto,
        domain=ProjectDetails,
        usecase=ProjectService,
        method="insert",
    ),
    "raw_node": RessourceLoader(
        dto=ProjectNodeDto,
        domain=ProjectNode,
        usecase=ProjectNodeService,
        method="insert_many",
    ),
    "node_meta": RessourceLoader(
        dto=ProjectNodeMetaImport,
        domain=ProjectNodeMeta,
        usecase=ProjectNodeMetaService,
        method="insert_many",
        perform_complex_mapping=MapProjectNodeMetaImportToDomain(),
    ),
}


@router.post("/import")
async def import_definitiown_set(
    file: UploadFile = File(...),
    injector=Depends(Inject(Injector)),
    mapper=Depends(Inject(Mapper)),
):
    async def load_ressources(
        ressource_type: str, ressource_specs: List[BaseModel]
    ) -> None:
        if len(ressource_specs) == 0:
            return

        ressource_loader = ressources[ressource_type]
        usecase = injector.get(ressource_loader.usecase)
        do_import = getattr(usecase, ressource_loader.method)
        ressources_domain = await ressource_loader.do_mapping(
            injector, mapper, ressource_specs
        )

        if ressource_loader.method.endswith("many"):
            await do_import(ressources_domain)
        else:
            for ressource_domain in ressources_domain:
                await do_import(ressource_domain)

    ressource_specs: List[BaseModel] = []
    last_ressource_type = None

    for line in file.file.readlines():
        ressource = loads(line)
        ressource_type = ressource["type"]
        ressource_payload = ressource["payload"]

        if not ressource_type in ressources:
            raise Exception(f"Ressource type not found: {ressource_type}")

        ressource_loader = ressources[ressource_type]
        ressource_spec = parse_obj_as(ressource_loader.dto, ressource_payload)

        if last_ressource_type is None:
            last_ressource_type = ressource_type
            ressource_specs.append(ressource_spec)
        elif last_ressource_type == ressource_type:
            ressource_specs.append(ressource_spec)
        else:
            await load_ressources(last_ressource_type, ressource_specs)
            last_ressource_type = ressource_type
            ressource_specs = [ressource_spec]

    await load_ressources(last_ressource_type, ressource_specs)
