from uuid import UUID
from typing import Any, List, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import mutation


@mutation.field("addTranslations")
@inject_graphql_route(create_translation)
@convert_kwargs_to_snake_case
async def resolve_add_translationst(
    _: Any,
    info: GraphQLResolveInfo,
    translations: List[dict],
    create_translation: callable,
):
    results = []
    for translation in translations:
        result = await create_translation(
            info, NewTranslationDto.parse_obj(translation)
        )
        results.append(result)

    return results


@mutation.field("updateTranslations")
@inject_graphql_route(update_translation)
@convert_kwargs_to_snake_case
async def resolve_update_translations(
    _: Any,
    info: GraphQLResolveInfo,
    translations: List[dict],
    update_translation: callable,
):
    results = []
    for translation in translations:
        result = await update_translation(info, TranslationDto.parse_obj(translation))
        results.append(result)

    return results
