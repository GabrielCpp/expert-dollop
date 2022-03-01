from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
    collapse_union,
)
from expert_dollup.app.controllers.project.project_node_meta import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from .types import query, mutation
from pydantic import parse_obj_as


@query.field("findProjectNodeMetaDefinition")
@inject_graphql_route(get_project_node_meta_definition)
@convert_kwargs_to_snake_case
async def find_project_node_meta_definition(
    parent: Any,
    info: GraphQLResolveInfo,
    project_id: str,
    node_id: str,
    get_project_node_meta_definition: callable,
):
    return await get_project_node_meta_definition(info, UUID(project_id), UUID(node_id))
