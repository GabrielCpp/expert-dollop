from fastapi import APIRouter, Depends, File, UploadFile
from uuid import UUID
from dataclasses import dataclass
from typing import Type, Optional, Callable, Any
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
        self, injector: Injector, mapper: Mapper, ressource_spec: BaseModel
    ) -> Any:
        if self.perform_complex_mapping is None:
            return mapper.map(ressource_spec, self.domain, self.dto)

        return await self.perform_complex_mapping(injector, ressource_spec)


class ProjectNodeMetaImport(BaseModel):
    project_id: UUID
    type_id: UUID
    state: ProjectNodeMetaStateDto


async def map_project_node_meta_import_to_domain(
    injector: Injector, model: ProjectNodeMetaImport
) -> ProjectNodeMeta:
    project_definition_node_service = injector.get(ProjectDefinitionNodeService)
    definition = await project_definition_node_service.find_by_id(model.type_id)
    return ProjectNodeMeta(
        project_id=model.project_id,
        type_id=model.type_id,
        state=ProjectNodeMetaState(**model.state.dict()),
        definition=definition,
    )


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
        usecase=LabelCollectionUseCase,
    ),
    "/api/label": RessourceLoader(
        dto=LabelDto,
        domain=Label,
        usecase=LabelUseCase,
    ),
    "/api/translation": RessourceLoader(
        dto=TranslationDto,
        domain=Translation,
        usecase=TranslationUseCase,
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
        method="insert",
    ),
    "node_meta": RessourceLoader(
        dto=ProjectNodeMetaImport,
        domain=ProjectNodeMeta,
        usecase=ProjectNodeMetaService,
        method="insert",
        perform_complex_mapping=map_project_node_meta_import_to_domain,
    ),
}


@router.post("/import")
async def import_definitiown_set(
    file: UploadFile = File(...),
    injector=Depends(Inject(Injector)),
    mapper=Depends(Inject(Mapper)),
):
    for line in file.file.readlines():
        ressource = loads(line)
        ressource_type = ressource["type"]
        ressource_payload = ressource["payload"]

        if not ressource_type in ressources:
            raise Exception(f"Ressource type not found: {ressource_type}")

        ressource_loader = ressources[ressource_type]
        ressource_spec = parse_obj_as(ressource_loader.dto, ressource_payload)
        usecase = injector.get(ressource_loader.usecase)
        do_import = getattr(usecase, ressource_loader.method)
        ressource_spec_domain = await ressource_loader.do_mapping(
            injector, mapper, ressource_spec
        )

        await do_import(ressource_spec_domain)
