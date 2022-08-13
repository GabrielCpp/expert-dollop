from typing import Union, List
from fastapi import Depends
from starlette.requests import Request
from uuid import UUID
from .auth_service import AuthService
from .inject_controller import Inject


class AuthenticationRequired:
    async def __call__(
        self, request: Request, auth: AuthService = Depends(Inject(AuthService))
    ):
        user = auth.authentification_required(request)
        return user


class CanPerformRequired:
    def __init__(self, permissions: Union[str, List[str]]):
        self.permissions = (
            permissions if isinstance(permissions, list) else [permissions]
        )

    async def __call__(
        self, request: Request, auth: AuthService = Depends(Inject(AuthService))
    ):
        user = await auth.can_perform_required(request, self.permissions)
        return user


class CanPerformOnRequired:
    def __init__(
        self,
        url_ressource: str,
        permissions: Union[str, List[str]],
        user_permissions: Union[str, List[str]] = [],
    ):
        self.url_ressource = url_ressource
        self.permissions = (
            permissions if isinstance(permissions, list) else [permissions]
        )
        self.user_permissions = (
            user_permissions
            if isinstance(user_permissions, list)
            else [user_permissions]
        )

    async def __call__(
        self, request: Request, auth: AuthService = Depends(Inject(AuthService))
    ):
        assert (
            self.url_ressource in request.path_params
        ), f"{self.url_ressource} not in url for {request.url}"
        ressource_id = request.path_params[self.url_ressource]
        user = await auth.can_perform_on_required(
            request, ressource_id, self.permissions, self.user_permissions
        )
        return user
