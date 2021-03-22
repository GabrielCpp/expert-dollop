from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.project.project_definition_node import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *

project_definition = ObjectType("ProjectDefinition")


@project_definition.field("viewableLayers")
@inject_graphql_route(find_viewable_layers)
@convert_kwargs_to_snake_case
async def resolve_viewabl_layers(
    _: Any,
    info: GraphQLResolveInfo,
    find_viewable_layers: callable,
    root_section_id: Optional[UUID] = None,
    sub_root_section_id: Optional[UUID] = None,
    form_id: Optional[UUID] = None,
):
    return await find_viewable_layers(
        info, root_section_id, sub_root_section_id, form_id
    )


types = [project_definition]