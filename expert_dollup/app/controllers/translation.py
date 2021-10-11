from typing import Optional
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain, HttpPageHandler
from expert_dollup.infra.services import TranslationService
from expert_dollup.app.dtos import (
    TranslationDto,
    TranslationIdDto,
    TranslationInputDto,
)
from expert_dollup.core.usecases import TranslationUseCase
from expert_dollup.core.domains import (
    Translation,
    TranslationId,
    TranslationRessourceLocaleQuery,
    TranslationFilter,
)

router = APIRouter()


@router.get("/translation/{ressource_id}/{scope}/{locale}/{name}")
async def find_translation(
    ressource_id: UUID,
    scope: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
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
    handler=Depends(Inject(RequestHandler)),
):
    id = TranslationId(ressource_id=ressource_id, locale=locale, scope=scope, name=name)
    await usecase.delete_by_id(id)


@router.get("/translation/{ressource_id}/{locale}")
async def get_all_translation_for_ressource(
    ressource_id: UUID,
    locale: str,
    handler=Depends(Inject(HttpPageHandler[TranslationService, TranslationDto])),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = 10,
):
    return await handler.handle(
        TranslationRessourceLocaleQuery(ressource_id=ressource_id, locale=locale),
        limit,
        next_page_token,
    )


@router.get("/translation/{ressource_id}/scope/{scope}")
async def find_translation_in_scope(
    ressource_id,
    scope,
    handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(TranslationService)),
):
    return await handler.handle_many(
        usecase.find_by,
        TranslationFilter(ressource_id=ressource_id, scope=scope),
        MappingChain(out_dto=TranslationDto, domain=Translation),
    )
