from fastapi import APIRouter, Depends, Query
from typing import Optional, Union
from uuid import UUID, uuid4
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.repositories import *
from expert_dollup.core.services import *

router = APIRouter()


@router.get("/definitions/{project_definition_id}/nodes/{id}")
async def find_project_definition_node(
    project_definition_id: UUID,
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.handle(
        usecase.find, id, MappingChain(out_dto=ProjectDefinitionNodeDto)
    )


@router.post("/definitions/{project_definition_id}/nodes")
async def create_project_definition_node(
    project_definition_id: UUID,
    project_definition_node: ProjectDefinitionNodeCreationDto,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    clock=Depends(Inject(Clock)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:create"])
    ),
):
    node = ProjectDefinitionNodeDto(
        id=uuid4(),
        project_definition_id=project_definition_id,
        creation_date_utc=clock.utcnow(),
        **project_definition_node.dict()
    )

    return await request_handler.handle(
        usecase.add,
        node,
        MappingChain(
            dto=ProjectDefinitionNodeDto,
            domain=ProjectDefinitionNode,
            out_dto=ProjectDefinitionNodeDto,
        ),
    )


@router.put("/definitions/{project_definition_id}/nodes/{node_id}")
async def update_project_definition_node(
    project_definition_id: UUID,
    node_id: UUID,
    creation_dto: ProjectDefinitionNodeCreationDto,
    usecase: ProjectDefinitionNodeUseCase = Depends(
        Inject(ProjectDefinitionNodeUseCase)
    ),
    request_handler=Depends(Inject(RequestHandler)),
    clock=Depends(Inject(Clock)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    node = ProjectDefinitionNodeDto(
        id=node_id,
        project_definition_id=project_definition_id,
        creation_date_utc=clock.utcnow(),
        **creation_dto.dict()
    )

    return await request_handler.handle(
        usecase.update,
        node,
        MappingChain(
            dto=ProjectDefinitionNodeDto,
            domain=ProjectDefinitionNode,
            out_dto=ProjectDefinitionNodeDto,
        ),
    )


@router.delete("/definitions/{project_definition_id}/nodes/{node_id}")
async def delete_project_definition_node(
    project_definition_id: UUID,
    node_id: UUID,
    usecase=Depends(
        Inject(ProjectDefinitionNodeUseCase),
    ),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:delete"])
    ),
):
    await usecase.delete(node_id)


@router.get("/definitions/{project_definition_id}/nodes")
async def get_project_definition_node_by_project(
    project_definition_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=100),
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await request_handler.forward(
        usecase.find_project_nodes,
        dict(
            next_page_token=next_page_token,
            limit=limit,
            project_definition_id=project_definition_id,
        ),
        MappingChain(
            out_domain=Page[ProjectDefinitionNode],
            out_dto=ProjectDefinitionNodePageDto,
        ),
    )


@router.get("/definitions/{project_definition_id}/root_sections")
async def find_definition_root_sections(
    project_definition_id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await request_handler.forward(
        usecase.find_root_sections,
        dict(project_definition_id=project_definition_id),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )


@router.get("/definitions/{project_definition_id}/root_section_nodes/{root_section_id}")
async def find_definition_root_section_nodes(
    project_definition_id: UUID,
    root_section_id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await request_handler.forward(
        usecase.find_root_section_nodes,
        dict(
            project_definition_id=project_definition_id,
            root_section_id=root_section_id,
        ),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )


@router.get("/definitions/{project_definition_id}/form_contents/{form_id}")
async def find_definition_form_content(
    project_definition_id: UUID,
    form_id: UUID,
    usecase=Depends(Inject(ProjectDefinitionNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await request_handler.forward(
        usecase.find_form_content,
        dict(project_definition_id=project_definition_id, form_id=form_id),
        MappingChain(
            out_domain=ProjectDefinitionNodeTree,
            out_dto=ProjectDefinitionNodeTreeDto,
        ),
    )


@router.post("/definitions/{project_definition_id}/formula_field_mix")
async def find_definition_formula_field_mix(
    project_definition_id: UUID,
    query: int = Query(alias="query", default=""),
    limit: int = Query(alias="limit", default=100),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler: PageHandlerProxy = Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[Union[ProjectDefinitionNode, Formula]])),
    repository=Depends(Inject(DefinitionNodeFormulaRepository)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.use_paginator(paginator).handle(
        CoreDefinitionNodeDto,
        repository.make_node_query(project_definition_id, query),
        limit,
        next_page_token,
    )
