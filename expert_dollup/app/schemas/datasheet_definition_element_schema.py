from uuid import UUID
from typing import Any, Optional
from ariadne import ObjectType, QueryType, convert_kwargs_to_snake_case, UnionType
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.handlers import GraphqlPageHandler
from expert_dollup.shared.starlette_injection import (
    inject_graphql_route,
    inject_graphql_handler,
)
from expert_dollup.app.controllers.datasheet.datasheet_controller import *
from expert_dollup.app.dtos import *
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_element_controller import *
from expert_dollup.app.controllers.datasheet.datasheet_definition_controller import *
from .types import datasheet_definition_element


@datasheet_definition_element.field("defaultProperties")
@convert_kwargs_to_snake_case
def resolve_default_properties(
    parent: DatasheetDefinitionElementDto,
    info: GraphQLResolveInfo,
):
    return [
        {"name": name, "property": str(property_value)}
        for name, property_value in parent.default_properties.items()
    ]
