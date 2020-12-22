from fastapi import APIRouter, Depends
from uuid import UUID
from predykt.shared.starlette_injection import Inject
from predykt.shared.handlers import RequestHandler
from predykt.app.dtos import TranslationDto, TranslationIdDto
from predykt.core.domains import Translation, TranslationId
from predykt.core.usecases import TranslationUseCase

router = APIRouter()


@router.get("/translation/{ressource_id}/{locale}/{name}")
async def get_translation(
    ressource_id: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    id = TranslationIdDto(ressource_id=ressource_id, locale=locale, name=name)
    return await handler.handle_with_result(id, TranslationIdDto, TranslationId, usecase.find_by_id, TranslationDto)


@router.post("/translation")
async def create_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle(translation, TranslationDto, Translation, usecase.add)


@router.put("/translation")
async def update_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle(translation, TranslationDto, Translation, usecase.update)


@router.delete("/translation/{ressource_id}/{locale}/{name}")
async def delete_translation(
    ressource_id: UUID,
    locale: str,
    name: str,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    id = TranslationId(ressource_id=ressource_id, locale=locale, name=name)
    await usecase.remove_by_id(id)
