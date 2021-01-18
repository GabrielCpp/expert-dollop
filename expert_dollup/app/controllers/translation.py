from typing import Optional
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.shared.database_services import Page
from expert_dollup.app.dtos import TranslationDto, TranslationIdDto, TranslationPageDto
from expert_dollup.core.usecases import TranslationUseCase
from expert_dollup.core.domains import (
    Translation,
    TranslationId,
    TranslationRessourceLocaleQuery,
    PaginatedRessource,
)

router = APIRouter()


@router.get("/translation/{ressource_id}/{locale}/{name}")
async def get_translation(
    ressource_id: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    id = TranslationIdDto(ressource_id=ressource_id, locale=locale, name=name)
    return await handler.handle(
        usecase.find_by_id,
        id,
        MappingChain(
            dto=TranslationIdDto, domain=TranslationId, out_dto=TranslationDto
        ),
    )


@router.post("/translation")
async def create_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add, translation, MappingChain(dto=TranslationDto, domain=Translation)
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


@router.delete("/translation/{ressource_id}/{locale}/{name}")
async def delete_translation(
    ressource_id: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    id = TranslationId(ressource_id=ressource_id, locale=locale, name=name)
    await usecase.remove_by_id(id)


@router.get("/translation/{ressource_id}/{locale}")
async def get_all_translation_for_ressource(
    ressource_id: UUID,
    locale: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = 10,
):
    query = TranslationRessourceLocaleQuery(ressource_id=ressource_id, locale=locale)

    return await handler.handle(
        usecase.find_by_ressource_locale,
        PaginatedRessource(next_page_token=next_page_token, limit=limit, query=query),
        MappingChain(out_domain=Page[Translation], out_dto=TranslationPageDto),
    )
