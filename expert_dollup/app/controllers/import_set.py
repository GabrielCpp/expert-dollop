from fastapi import APIRouter, Depends, File, UploadFile
from dataclasses import dataclass, fields
from typing import Callable, Type
from pydantic.tools import parse_obj_as
from injector import Injector
from pydantic import create_model, BaseModel
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.usecases import *
from json import loads
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.automapping import Mapper

router = APIRouter()


@dataclass
class RessourceLoader:
    dto: Type
    domain: Type
    usecase: Type
    method: str = "add"


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
        dto=FormulaDto,
        domain=Formula,
        usecase=FormulaUseCase,
    ),
}


@router.post("/import/definition")
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
        ressource_spec_domain = mapper.map(
            ressource_spec, ressource_loader.domain, ressource_loader.dto
        )

        await do_import(ressource_spec_domain)
