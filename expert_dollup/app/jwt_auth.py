from jwt import encode, decode, DecodeError
from typing import Union, List
from fastapi import Depends
from starlette.requests import Request
from uuid import UUID
from .settings import AppSettings
from expert_dollup.core.domains import RessourceId, Ressource, User
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.shared.starlette_injection import DetailedError, AuthService, Inject
from expert_dollup.shared.database_services import RecordNotFound

BEARER_AUTH = "Bearer"


class NoBearerAuthorizationHeader(Exception):
    def __init__(self):
        Exception.__init__(self, "No Bearer Authorization token.")


class InvalidBearerToken(DetailedError):
    pass


class PermissionMissing(DetailedError):
    pass


class AuthJWT(AuthService):
    def __init__(
        self,
        settings: AppSettings,
        user_service: CollectionService[User],
        ressource_service: CollectionService[Ressource],
    ):
        self.settings = settings
        self.user_service = user_service
        self.ressource_service = ressource_service

    def authentification_required(self, request: Request):
        authorization_header = request.headers.get("Authorization", "")

        if not authorization_header.startswith(BEARER_AUTH):
            raise NoBearerAuthorizationHeader()

        token = authorization_header[len(BEARER_AUTH) :].strip()

        try:
            decoded = decode(
                token,
                self.settings.authjwt_public_key,
                audience=self.settings.authjwt_decode_audience,
                algorithms=[self.settings.authjwt_algorithm],
            )
        except DecodeError as e:
            raise InvalidBearerToken("Invalid bearer token", reason=str(e))

        return decoded

    async def can_perform_on_required(
        self,
        request: Request,
        ressource_id: UUID,
        permissions: Union[str, List[str]],
        user_permissions: Union[str, List[str]] = [],
    ):
        user = await self.can_perform_required(request, user_permissions)

        try:
            ressource = await self.ressource_service.find_by_id(
                RessourceId(ressource_id, user.id)
            )
        except RecordNotFound:
            raise PermissionMissing(
                "Permission missing", reason="user has not access to ressource."
            )

        for permission in permissions:
            if permission.startswith("*"):
                permission = ressource.kind + permission[1:]

            if not permission in ressource.permissions:
                raise PermissionMissing("Permission missing", reason=permission)

        return user

    async def can_perform_required(
        self, request: Request, permissions: Union[str, List[str]]
    ):
        oauth_id = self.authentification_required(request).get("sub")

        try:
            user = await self.user_service.find_by_id(oauth_id)
        except RecordNotFound:
            raise PermissionMissing("Permission missing", reason="user missing")

        for permission in permissions:
            if not permission in user.permissions:
                raise PermissionMissing("Permission missing", reason=permission)

        return user

    def make_token(self, oauth_id: str) -> str:
        return encode(
            {"aud": self.settings.authjwt_decode_audience, "sub": oauth_id},
            self.settings.authjwt_private_key.encode("ascii"),
            algorithm=self.settings.authjwt_algorithm,
        )
