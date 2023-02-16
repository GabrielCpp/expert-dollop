from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.core.usecases import *
from expert_dollup.app.dtos import *


router = APIRouter()


@router.get("/definitions")
async def find_paginated_project_definitions(
    query: str = Query(alias="query", default=""),
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    paginator=Depends(Inject(UserRessourcePaginator[ProjectDefinition])),
    handler: PageHandlerProxy = Depends(Inject(PageHandlerProxy)),
    user=Depends(CanPerformRequired(["project_definition:get"])),
):
    return await handler.use_paginator(paginator).handle(
        ProjectDefinitionDto,
        UserRessourceQuery(organization_id=user.organization_id, names=query.split()),
        limit,
        next_page_token,
    )


@router.get("/definitions/{project_definition_id}")
async def find_project_definition(
    project_definition_id: UUID,
    usecase: ProjectDefinitonUseCase = Depends(Inject(ProjectDefinitonUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.handle(
        usecase.find,
        project_definition_id,
        MappingChain(out_dto=ProjectDefinitionDto),
    )


@router.post("/definitions")
async def create_project_definition(
    new_definition: NewDefinitionDto,
    usecase: ProjectDefinitonUseCase = Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("project_definition:create")),
):
    return await request_handler.forward_mapped(
        usecase.add,
        dict(domain=new_definition, user=user),
        MappingChain(out_dto=ProjectDefinitionDto),
        map_keys=dict(
            domain=MappingChain(
                dto=NewDefinitionDto,
                domain=ProjectDefinition,
            ),
        ),
    )


@router.put("/definitions/{project_definition_id}")
async def update_project_definition(
    project_definition: NewDefinitionDto,
    usecase: ProjectDefinitonUseCase = Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await request_handler.handle(
        usecase.update,
        project_definition,
        MappingChain(
            dro=NewDefinitionDto,
            domain=ProjectDefinition,
            out_dto=ProjectDefinitionDto,
        ),
    )


@router.delete("/definitions/{project_definition_id}")
async def delete_project_definition(
    project_definition_id: UUID,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:delete"])
    ),
):
    await usecase.delete(project_definition_id)
