from fastapi import APIRouter, Depends, File, UploadFile
from uuid import UUID
from dataclasses import dataclass
from typing import Type, Optional, Callable, Any, List
from pydantic.main import BaseModel
from pydantic.tools import parse_obj_as
from injector import Injector
from json import loads
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.automapping import Mapper
from expert_dollup.core.utils.ressource_permissions import make_ressource
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.usecases import *
from expert_dollup.core.builders import *
from expert_dollup.core.logits import *
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

    async def load_ressources(
        self, injector: Injector, ressource_specs: List[BaseModel], user: User
    ) -> None:
        if len(ressource_specs) == 0:
            return

        mapper = injector.get(Mapper)
        usecase = injector.get(self.usecase)
        do_import = getattr(usecase, self.method)
        ressources_domain = await self.do_mapping(injector, mapper, ressource_specs)

        if self.method.endswith("many") or self.method.endswith("s"):
            await do_import(ressources_domain)
        else:
            for ressource_domain in ressources_domain:
                await do_import(ressource_domain)


@dataclass
class ImportRessource:
    dto: Type
    domain: Type
    usecase: Type
    method: str = "add"

    async def load_ressources(
        self, injector: Injector, ressource_specs: List[BaseModel], user: User
    ) -> None:
        if len(ressource_specs) == 0:
            return

        mapper = injector.get(Mapper)
        usecase = injector.get(self.usecase)
        do_import = getattr(usecase, self.method)
        ressources_domain = mapper.map_many(ressource_specs, self.domain, self.dto)

        if self.method.endswith("many") or self.method.endswith("s"):
            await do_import(ressources_domain, user)
        else:
            for ressource_domain in ressources_domain:
                await do_import(ressource_domain, user)


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

        defs = self.node_by_project_id[project_id]

        return [
            ProjectNodeMeta(
                project_id=model.project_id,
                type_id=model.type_id,
                state=ProjectNodeMetaState(**model.state.dict()),
                definition=defs[model.type_id],
            )
            for model in models
        ]


class InsertProjectWithRessourceAction:
    def __init__(self):
        self.dto = ProjectDetailsDto
        self.domain = ProjectDetails

    async def load_ressources(
        self, injector: Injector, ressource_specs: List[BaseModel], user: User
    ) -> None:
        ressource_service = injector.get(CollectionService[Ressource])
        project_service = injector.get(ProjectService)
        mapper = injector.get(Mapper)

        for ressource_spec in ressource_specs:
            project_details = mapper.map(ressource_spec, ProjectDetails)
            await ressource_service.insert(
                make_ressource(
                    ProjectDetails,
                    project_details,
                    user.id,
                )
            )
            await project_service.insert(project_details)


class DedupTranslations:
    def clear(self):
        self.node_by_project_id = {}

    async def __call__(
        self, injector: Injector, models: List[ProjectNodeMetaImport]
    ) -> List[ProjectNodeMeta]:
        if len(models) == 0:
            return

        mapper = injector.get(Mapper)
        translations = mapper.map_many(models, Translation)

        seen = {}
        translations = [
            seen.setdefault(
                (
                    translation.ressource_id,
                    translation.scope,
                    translation.locale,
                    translation.name,
                ),
                translation,
            )
            for translation in translations
            if not (
                translation.ressource_id,
                translation.scope,
                translation.locale,
                translation.name,
            )
            in seen
        ]

        return translations


class RecreateFormulaCacheDto(BaseModel):
    project_def_id: UUID
    project_id: UUID


ressources = {
    "/api/datasheet_definition": ImportRessource(
        dto=DatasheetDefinitionDto,
        domain=DatasheetDefinition,
        usecase=DatasheetDefinitionUseCase,
    ),
    "/api/datasheet": ImportRessource(
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
        perform_complex_mapping=DedupTranslations(),
    ),
    "/api/datasheet_definition_element": RessourceLoader(
        dto=DatasheetDefinitionElementDto,
        domain=DatasheetDefinitionElement,
        usecase=DatasheetDefinitionElementUseCase,
    ),
    "/api/project_definition": ImportRessource(
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
        method="add_many",
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
    "raw_project": InsertProjectWithRessourceAction(),
    "raw_node": RessourceLoader(
        dto=ProjectNodeDto,
        domain=ProjectNode,
        usecase=ProjectNodeUseCase,
        method="imports",
    ),
    "node_meta": RessourceLoader(
        dto=ProjectNodeMetaImport,
        domain=ProjectNodeMeta,
        usecase=ProjectNodeMetaService,
        method="insert_many",
        perform_complex_mapping=MapProjectNodeMetaImportToDomain(),
    ),
}


@router.post("/import/{user_id}")
async def import_definitiown_set(
    user_id: UUID,
    file: UploadFile = File(...),
    injector=Depends(Inject(Injector)),
    user_service=Depends(Inject(CollectionService[User])),
):
    ressource_specs: List[BaseModel] = []
    last_ressource_type = None
    user = await user_service.find_one_by(UserFilter(id=user_id))

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
            await ressources[last_ressource_type].load_ressources(
                injector, ressource_specs, user
            )
            last_ressource_type = ressource_type
            ressource_specs = [ressource_spec]

    await ressources[last_ressource_type].load_ressources(
        injector, ressource_specs, user
    )
