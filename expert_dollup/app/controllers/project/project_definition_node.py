import structlog
from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.app.dtos import (
    ProjectDefinitionNodeDto,
    ProjectDefinitionNodePageDto,
    ProjectDefinitionNodeTreeDto,
)
from expert_dollup.core.domains import (
    ProjectDefinitionNode,
    ProjectDefinitionNodeTree,
)
from expert_dollup.core.usecases import ProjectDefinitonContainerUseCase
from expert_dollup.shared.database_services import Page

router = APIRouter()


@router.get("/project_definition_node/{id}")
async def get_project_definition_node(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectDefinitionNodeDto)
    )


@router.post("/project_definition_node")
async def create_project_definition_node(
    project_definition_node: ProjectDefinitionNodeDto,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.add,
        project_definition_node,
        MappingChain(
            dto=ProjectDefinitionNodeDto,
            domain=ProjectDefinitionNode,
            out_dto=ProjectDefinitionNodeDto,
        ),
    )


@router.put("/project_definition_node")
async def replace_project_definition_node(
    project_definition_node: ProjectDefinitionNodeDto,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.update,
        project_definition_node,
        MappingChain(
            dto=ProjectDefinitionNodeDto,
            domain=ProjectDefinitionNode,
            out_dto=ProjectDefinitionNodeDto,
        ),
    )


@router.delete("/project_definition_node/{id}")
async def delete_project_definition_node(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    await usecase.remove_by_id(id)


@router.get("/{project_def_id}/project_definition_nodes")
async def get_project_definition_node_by_project(
    project_def_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=100),
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
):
    return await request_handler.forward(
        usecase.find_project_containers,
        dict(
            next_page_token=next_page_token,
            limit=limit,
            project_def_id=project_def_id,
        ),
        MappingChain(
            out_domain=Page[ProjectDefinitionNode],
            out_dto=ProjectDefinitionNodePageDto,
        ),
    )


@router.get("/project_definition/viewable_layers")
async def find_viewable_layers(
    root_section_id: Optional[UUID] = Query(alias="rootSectionId", default=None),
    sub_root_section_id: Optional[UUID] = Query(alias="subRootSectionId", default=None),
    form_id: Optional[UUID] = Query(alias="formId", default=None),
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_viewable_layers,
        dict(
            root_section_id=root_section_id,
            sub_root_section_id=sub_root_section_id,
            form_id=form_id,
        ),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )
