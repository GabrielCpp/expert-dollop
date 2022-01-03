from ariadne.types import GraphQLResolveInfo
from expert_dollup.shared.starlette_injection import GraphqlContext
from expert_dollup.app.dtos import *
from .types import field_value, field_details_union_type


@field_value.type_resolver
def resolve_field_value_type(
    target: PrimitiveWithNoneUnionDto, info: GraphQLResolveInfo, context: GraphqlContext
):
    target_type = type(target)

    if not target_type in value_type_lookup_map:
        raise LookupError(f"Field type not found {target_type}")

    return value_type_lookup_map[target_type]


@field_details_union_type.type_resolver
def resolve_field_details_union_type(
    target: FieldDetailsUnionDto, info: GraphQLResolveInfo, context: GraphqlContext
):
    target_type = type(target)

    if not target_type in config_type_lookup_map:
        raise LookupError("Field type not found")

    return config_type_lookup_map[target_type]
