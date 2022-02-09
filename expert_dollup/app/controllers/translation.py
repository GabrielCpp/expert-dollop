from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.database_services import Paginator, CollectionService
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    MappingChain,
    HttpPageHandler,
    Inject,
    CanPerformOnRequired,
    CanPerformRequired,
)
from expert_dollup.core.usecases import TranslationUseCase
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *

router = APIRouter()


@router.get("/translation/{ressource_id}/{scope}/{locale}/{name}")
async def find_translation(
    ressource_id: UUID,
    scope: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("ressource_id", "*:read")),
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


@router.post("/translation")
async def create_translation(
    translation: TranslationInputDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("translation:create")),
):
    return await handler.handle(
        usecase.add,
        translation,
        MappingChain(dto=TranslationInputDto, domain=Translation),
    )


@router.put("/translation")
async def update_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("translation:create")),
):
    return await handler.handle(
        usecase.update,
        translation,
        MappingChain(dto=TranslationDto, domain=Translation),
    )


@router.delete("/translation/{ressource_id}/{scope}/{locale}/{name}")
async def delete_translation(
    ressource_id: UUID,
    scope: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    user=Depends(CanPerformRequired("translation:delete")),
):
    id = TranslationId(ressource_id=ressource_id, locale=locale, scope=scope, name=name)
    await usecase.delete_by_id(id)


@router.get("/translation/{ressource_id}/{locale}")
async def get_all_translation_for_ressource(
    ressource_id: UUID,
    locale: str,
    handler=Depends(Inject(HttpPageHandler[Paginator[Translation]])),
    user=Depends(CanPerformRequired("translation:read")),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = 10,
):
    return await handler.handle(
        TranslationDto,
        TranslationRessourceLocaleQuery(ressource_id=ressource_id, locale=locale),
        limit,
        next_page_token,
    )


@router.get("/translation/{ressource_id}/scope/{scope}")
async def find_translation_in_scope(
    ressource_id,
    scope,
    handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(CollectionService[Translation])),
    user=Depends(CanPerformRequired("translation:read")),
):
    return await handler.handle_many(
        usecase.find_by,
        TranslationFilter(ressource_id=ressource_id, scope=scope),
        MappingChain(out_dto=TranslationDto, domain=Translation),
    )


@router.get("/translation/{ressource_id}/{locale}/json_bundle")
async def get_json_bundle_for_ressource_locale(
    ressource_id: UUID,
    locale: str,
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: TranslationUseCase = Depends(Inject(TranslationUseCase)),
    user=Depends(CanPerformRequired("translation:read")),
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
