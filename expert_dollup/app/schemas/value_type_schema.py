from uuid import UUID
from typing import Any, Optional
from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlContext
from expert_dollup.app.dtos import *
from .types import field_value, node_config_value_type


@field_value.type_resolver
def resolve_field_value_type(
    target: ValueUnionDto, info: GraphQLResolveInfo, context: GraphqlContext
):
    if isinstance(target, IntFieldValueDto):
        return "IntFieldValue"
    elif isinstance(target, DecimalFieldValueDto):
        return "DecimalFieldValue"
    elif isinstance(target, StringFieldValueDto):
        return "StringFieldValue"
    elif isinstance(target, BoolFieldValueDto):
        return "BoolFieldValue"
    elif not target is None:
        raise LookupError("Field type not found")

    return "null"


config_type_lookup_map = {
    IntFieldConfigDto: "IntFieldConfig",
    DecimalFieldConfigDto: "DecimalFieldConfig",
    StringFieldConfigDto: "StringFieldConfig",
    BoolFieldConfigDto: "BoolFieldConfig",
    StaticChoiceFieldConfigDto: "StaticChoiceFieldConfig",
    CollapsibleContainerFieldConfigDto: "CollapsibleContainerFieldConfig",
    type(None): "null",
}


@node_config_value_type.type_resolver
def resolve_node_config_value_type(
    target: NodeConfigValueType, info: GraphQLResolveInfo, context: GraphqlContext
):
    target_type = type(target)

    if not target_type in config_type_lookup_map:
        raise LookupError("Field type not found")

    return config_type_lookup_map[target_type]
