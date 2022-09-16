from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import *
from expert_dollup.app.controllers.translation import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from .types import project_node_meta
from pydantic import parse_obj_as


@project_node_meta.field("translations")
@inject_graphql_route(find_translation_in_scope)
async def resolve_project_definition_node_translations(
    parent: ProjectNodeMeta,
    info: GraphQLResolveInfo,
    find_translation_in_scope: callable,
):
    return await find_translation_in_scope(
        info, parent.definition.project_definition_id, parent.definition.id
    )
