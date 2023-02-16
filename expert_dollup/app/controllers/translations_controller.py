from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.usecases import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *

router = APIRouter()


@router.get("/definitions/{ressource_id}/translations/{locale}/{name}")
async def find_translation(
    ressource_id: UUID,
    locale: str,
    name: str,
    usecase: TranslationUseCase = Depends(Inject(TranslationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("ressource_id", "project_definition:get")),
):

    return await handler.do_handle(
        usecase.find,
        MappingChain(dto=TranslationDto, domain=Translation),
        ressource_id=ressource_id,
        locale=locale,
        name=name,
    )


@router.get("/definitions/{ressource_id}/translations")
async def find_paginated_translations(
    ressource_id: UUID,
    locale: Optional[str] = Query(alias="locale", default=None),
    scope: Optional[UUID] = Query(alias="scope", default=None),
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler=Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[Translation])),
    user=Depends(CanPerformOnRequired("ressource_id", "project_definition:get")),
):
    query_filter = TranslationFilter(ressource_id=ressource_id)
    query_filter.put_when_present("locale", locale)
    query_filter.put_when_present("scope", scope)

    return await handler.use_paginator(paginator).handle(
        TranslationDto,
        query_filter,
        limit,
        next_page_token,
    )


@router.post("/definitions/{definition_id}/translations")
async def create_translation(
    definition_id: UUID,
    new_translation: NewTranslationDto,
    usecase: TranslationUseCase = Depends(Inject(TranslationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("definition_id", "project_definition:update")),
):
    return await handler.do_handle(
        usecase.add,
        MappingChain(dto=TranslationDto, domain=Translation),
        definition_id=definition_id,
        new_translation=MappingChain(
            dto=NewTranslationDto, domain=NewTranslation, value=new_translation
        ),
    )


@router.put("/definitions/{definition_id}/translations")
async def update_translation(
    definition_id: UUID,
    translation: NewTranslationDto,
    usecase=Depends(Inject(TranslationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("definition_id", "project_definition:update")),
):
    return await handler.do_handle(
        usecase.update,
        MappingChain(dto=TranslationDto, domain=Translation),
        definition_id=definition_id,
        replacement=MappingChain(
            dto=NewTranslationDto, domain=NewTranslation, value=new_translation
        ),
    )


@router.delete("/definitions/{ressource_id}/translations/{locale}/{name}")
async def delete_translation(
    ressource_id: UUID,
    locale: str,
    name: str,
    usecase: TranslationUseCase = Depends(Inject(TranslationUseCase)),
    user=Depends(CanPerformOnRequired("ressource_id", "project_definition:update")),
):
    await usecase.delete(ressource_id=ressource_id, locale=locale, name=name)


@router.get("/translations/{ressource_id}")
async def find_translation_in_scope(
    ressource_id: UUID,
    scope: Optional[UUID] = Query(alias="scope", default=None),
    repository: Repository[Translation] = Depends(Inject(Repository[Translation])),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("ressource_id", "*:get", [])),
):
    return await handler.do_handle(
        repository.find_by,
        MappingChain(dto=List[TranslationDto], domain=List[Translation]),
        query_filter=TranslationFilter(ressource_id=ressource_id, scope=scope),
    )


@router.get("/translations/{ressource_id}/json_bundle")
async def get_json_bundle_for_ressource_locale(
    ressource_id: UUID,
    locale: str = Query(alias="locale", default="en-US"),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: TranslationUseCase = Depends(Inject(TranslationUseCase)),
    user=Depends(CanPerformOnRequired("ressource_id", "*:get", [])),
):
    return await handler.do_handle(
        usecase.get_translation_bundle,
        MappingChain(dto=dict, domain=List[Translation]),
        ressource_id=ressource_id,
        locale=locale,
        user=user,
    )
