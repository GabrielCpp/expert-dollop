from functools import wraps
from typing import List
from expert_dollup.shared.fastapi_jwt_auth import AuthJWT


def secure_graphql_route(permissions: List[str] = [], permission_claim: str = "roles"):
    def decorate(fn):
        @wraps(fn)
        def check_permissions(*args, **kwargs):
            jwt_service = args[1].context.container.get(AuthJWT)
            jwt_service.jwt_required()
            decoded_token = jwt_service.get_raw_jwt()

            if not permission_claim in decoded_token:
                raise Exception("Missing permissions")

            granted_permissions = decoded_token[permission_claim]

            if not isinstance(granted_permissions, list) or not all(
                permission in granted_permissions for permission in permissions
            ):
                raise Exception("Missing permissions")

            return fn(*args, **kwargs)

        return check_permissions

    return decorate


# secure_ressource
