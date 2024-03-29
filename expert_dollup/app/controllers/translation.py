from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.usecases import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *

router = APIRouter()


@router.get("/translations/{ressource_id}/{scope}/{locale}/{name}")
async def find_translation(
    ressource_id: UUID,
    scope: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("ressource_id", "*:get", [])),
):
    id = TranslationIdDto(
        ressource_id=ressource_id, scope=scope, locale=locale, name=name
    )

    return await handler.handle(
        usecase.find_by_id,
        id,
        MappingChain(
            dto=TranslationIdDto, domain=TranslationId, out_dto=TranslationDto
        ),
    )


@router.post("/translations")
async def create_translation(
    translation: TranslationInputDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("project_definition:update")),
):
    return await handler.handle(
        usecase.add,
        translation,
        MappingChain(dto=TranslationInputDto, domain=Translation),
    )


@router.put("/translations")
async def update_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("project_definition:update")),
):
    return await handler.handle(
        usecase.update,
        translation,
        MappingChain(dto=TranslationDto, domain=Translation),
    )


@router.delete("/translations/{ressource_id}/{scope}/{locale}/{name}")
async def delete_translation(
    ressource_id: UUID,
    scope: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    user=Depends(CanPerformRequired("project_definition:update")),
):
    id = TranslationId(ressource_id=ressource_id, locale=locale, scope=scope, name=name)
    await usecase.delete_by_id(id)


@router.get("/translations/{ressource_id}/{locale}")
async def get_all_translation_for_ressource(
    ressource_id: UUID,
    locale: str,
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler=Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[Translation])),
    user=Depends(CanPerformRequired("project_definition:get")),
):
    return await handler.use_paginator(paginator).handle(
        TranslationDto,
        TranslationRessourceLocaleQuery(ressource_id=ressource_id, locale=locale),
        limit,
        next_page_token,
    )


@router.get("/translations/{ressource_id}/scopes/{scope}")
async def find_translation_in_scope(
    ressource_id: UUID,
    scope: UUID,
    handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(Repository[Translation])),
    user=Depends(CanPerformOnRequired("ressource_id", "*:get", [])),
):
    return await handler.handle_many(
        usecase.find_by,
        TranslationFilter(ressource_id=ressource_id, scope=scope),
        MappingChain(out_dto=TranslationDto, domain=Translation),
    )


@router.get("/translations/{ressource_id}/{locale}/json_bundle")
async def get_json_bundle_for_ressource_locale(
    ressource_id: UUID,
    locale: str,
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: TranslationUseCase = Depends(Inject(TranslationUseCase)),
    user=Depends(CanPerformOnRequired("ressource_id", "*:get", [])),
):
    return await handler.forward(
        usecase.get_translation_bundle,
        {
            "query": TranslationRessourceLocaleQuery(
                ressource_id=ressource_id, locale=locale
            ),
            "user": user,
        },
        MappingChain(out_dto=dict, out_domain=List[Translation]),
    )
