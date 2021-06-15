from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.usecases import ProjectNodeUseCase
from expert_dollup.core.domains import (
    ProjectNodeFilter,
    ValueUnion,
    ProjectNodeTree,
)
from expert_dollup.app.dtos import (
    ProjectNodeDto,
    ProjectNodeTreeDto,
    ProjectNodeCollectionTargetDto,
    ValueUnionDto,
    ProjectNodeTreeDto,
)

router = APIRouter()


@router.get("/project/{project_id}/container/{node_id}")
async def get_project_node(
    project_id: UUID,
    node_id: UUID,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, node_id, MappingChain(out_dto=ProjectNodeDto)
    )


@router.get("/project/{project_id}/containers")
async def find_project_nodes_by(
    project_id: UUID,
    type_id: UUID = Query(alias="typeId", default=None),
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_many(
        usecase.find_by_type,
        {"project_id": project_id, "type_id": type_id},
        MappingChain(out_dto=ProjectNodeDto),
    )


@router.get("/project/{project_id}/children")
async def find_project_children_tree(
    project_id: UUID,
    path: List[UUID] = Query(alias="path", default=[]),
    level: int = Query(alias="level", default=None),
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_many(
        usecase.find_by_path,
        {"project_id": project_id, "path": path, "level": level},
        MappingChain(out_dto=ProjectNodeDto),
    )


@router.get("/project/{project_id}/subtree")
async def find_project_subtree(
    project_id: UUID,
    path: List[UUID] = Query(alias="path", default=[]),
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_many(
        usecase.find_subtree,
        {"project_id": project_id, "path": path},
        MappingChain(out_dto=ProjectNodeDto),
    )


@router.get("/project/{project_id}/roots")
async def find_root_sections(
    project_id: UUID,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_root_sections,
        dict(project_id=project_id),
        MappingChain(
            out_domain=ProjectNodeTree,
            out_dto=ProjectNodeTreeDto,
        ),
    )


@router.get("/project/{project_id}/root_section_nodes/{root_section_id}")
async def find_root_section_nodes(
    project_id: UUID,
    root_section_id: UUID,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_root_section_nodes,
        dict(
            project_id=project_id,
            root_section_id=root_section_id,
        ),
        MappingChain(
            out_domain=ProjectNodeTree,
            out_dto=ProjectNodeTreeDto,
        ),
    )


@router.get("/project/{project_id}/form/{form_id}")
async def find_form_content(
    project_id: UUID,
    form_id: UUID,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.forward(
        usecase.find_form_content,
        dict(project_id=project_id, form_id=form_id),
        MappingChain(
            out_domain=ProjectNodeTree,
            out_dto=ProjectNodeTreeDto,
        ),
    )


@router.put("/project/{project_id}/container/{node_id}/value")
async def mutate_project_field(
    project_id: UUID,
    node_id: UUID,
    value: ValueUnionDto,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_mapped(
        usecase.update_node_value,
        dict(project_id=project_id, node_id=node_id, value=value),
        MappingChain(out_dto=ProjectNodeTreeDto),
        map_keys=dict(value=MappingChain(dto=ValueUnionDto, domain=ValueUnion)),
    )


@router.post("/project/{project_id}/container/collection")
async def add_project_collection(
    project_id: UUID,
    collection_target: ProjectNodeCollectionTargetDto,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_many(
        usecase.add_collection,
        {"project_id": project_id, **collection_target.dict()},
        MappingChain(out_dto=ProjectNodeDto),
    )


@router.post("/project/{project_id}/container/{collection_node_id}/clone")
async def clone_project_collection(
    project_id: UUID,
    collection_node_id: UUID,
    usecase=Depends(Inject(ProjectNodeUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_many(
        usecase.clone_collection,
        {"project_id": project_id, "node_id": collection_node_id},
        MappingChain(out_dto=ProjectNodeDto),
    )


@router.delete("/project/{project_id}/container/{node_id}")
async def remove_project_node_collection(
    project_id: UUID,
    node_id: UUID,
    usecase=Depends(Inject(ProjectNodeUseCase)),
):
    await usecase.remove_collection(project_id, node_id)