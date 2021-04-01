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
from expert_dollup.core.usecases import ProjectDefinitionNodeUseCase
from expert_dollup.shared.database_services import Page
from expert_dollup.infra.services import ProjectDefinitionNodeService

router = APIRouter()


@router.get("/project_definition/{project_def_id}/node/{id}")
async def find_project_definition_node(
    project_def_id: UUID,
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectDefinitionNodeDto)
    )


@router.post("/project_definition_node")
async def create_project_definition_node(
    project_definition_node: ProjectDefinitionNodeDto,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
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
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
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


@router.delete("/project_definition/{project_def_id}/node/{id}")
async def delete_project_definition_node(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    await usecase.remove_by_id(id)


@router.get("/{project_def_id}/project_definition_nodes")
async def get_project_definition_node_by_project(
    project_def_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=100),
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
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


@router.get("/project_definition/{project_def_id}/root_sections")
async def find_root_sections(
    project_def_id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_root_sections,
        dict(project_def_id=project_def_id),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )


@router.get(
    "/project_definition/{project_def_id}/root_section_containers/{root_section_id}"
)
async def find_root_section_containers(
    project_def_id: UUID,
    root_section_id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_root_section_containers,
        dict(
            project_def_id=project_def_id,
            root_section_id=root_section_id,
        ),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )


@router.get("/project_definition/{project_def_id}/form_content/{form_id}")
async def find_form_content(
    project_def_id: UUID,
    form_id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_form_content,
        dict(project_def_id=project_def_id, form_id=form_id),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )
