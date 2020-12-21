from fastapi import APIRouter, Depends
from uuid import UUID
from predykt.shared.starlette_injection import Inject
from predykt.shared.handlers import RequestHandler
from predykt.app.dtos import TranslationDto
from predykt.core.domains import Translation
from predykt.core.usecases import TranslationUseCase

router = APIRouter()


@router.get("/translation/{id}")
async def get_translation(
    id: UUID,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle_id_with_result(id, usecase.find_by_id, TranslationDto)


@router.post("/translation")
async def create_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(translation, TranslationDto, Translation, usecase.insert)


@router.put("/translation")
async def update_translation(
    translation: TranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(translation, TranslationDto, Translation, usecase.update)


@router.delete("/translation/{id}")
async def delete_translation(
    id: UUID,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    await usecase.delete_by_id(id)
