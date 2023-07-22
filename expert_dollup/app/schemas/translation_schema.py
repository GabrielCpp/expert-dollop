from uuid import UUID
from typing import Any, List, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.translations_controller import *
from expert_dollup.app.dtos import *
from .types import mutation


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
