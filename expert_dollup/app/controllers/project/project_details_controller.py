from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID, uuid4
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.core.services import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/projects")
async def find_paginated_project_details(
    query: str = Query(alias="query", default=""),
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    paginator=Depends(Inject(UserRessourcePaginator[ProjectDetails])),
    handler: PageHandlerProxy = Depends(Inject(PageHandlerProxy)),
    user=Depends(CanPerformRequired(["project:get"])),
):
    return await handler.use_paginator(paginator).handle(
        ProjectDetailsDto,
        UserRessourceQuery(organization_id=user.organization_id, names=query.split()),
        limit,
        next_page_token,
    )


@router.get("/projects/{project_id}")
async def find_project_details(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("project_id", ["project:get"])),
):
    return await handler.handle(
        usecase.find, project_id, MappingChain(out_dto=ProjectDetailsDto)
    )


@router.post("/projects")
async def create_project(
    project: ProjectDetailsInputDto,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("project:create")),
):
    return await handler.forward_mapped(
        usecase.add,
        dict(project_details=project, user=user),
        MappingChain(out_dto=ProjectDetailsDto),
        map_keys=dict(
            project_details=MappingChain(
                dto=ProjectDetailsInputDto,
                domain=ProjectDetails,
            ),
        ),
    )


@router.post("/projects/{project_id}/clone")
async def clone_project(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_id", ["project:get"], ["project:clone"])
    ),
):
    return await handler.forward(
        usecase.clone,
        dict(project_id=project_id, user=user),
        MappingChain(out_dto=ProjectDetailsDto),
    )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    user=Depends(CanPerformOnRequired("project_id", ["project:delete"])),
):
    await usecase.delete(project_id)
