from jwt import encode, decode, DecodeError
from jwt.algorithms import get_default_algorithms
from typing import Union, List, Dict, Any, Optional
from starlette.requests import Request
from uuid import UUID
from .settings import AppSettings
from expert_dollup.core.domains import RessourceId, Ressource, User
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.shared.starlette_injection import DetailedError, AuthService, Inject
from expert_dollup.shared.database_services import RecordNotFound

BEARER_AUTH = "Bearer"
ALGORITHM = "RS256"


class NoBearerAuthorizationHeader(Exception):
    def __init__(self):
        Exception.__init__(self, "No Bearer Authorization token.")


class InvalidBearerToken(DetailedError):
    pass


class PermissionMissing(DetailedError):
    pass


class AuthJWT(AuthService[User]):
    def __init__(
        self,
        settings: AppSettings,
        user_service: CollectionService[User],
        ressource_service: CollectionService[Ressource],
    ):
        self.settings = settings
        self.user_service = user_service
        self.ressource_service = ressource_service

    def authentification_optional(self, request: Request) -> Optional[Dict[str, Any]]:
        try:
            return self.authentification_required(request)
        except NoBearerAuthorizationHeader:
            return None

    def authentification_required(self, request: Request) -> Dict[str, Any]:
        authorization_header = request.headers.get("Authorization", "")

        if not authorization_header.startswith(BEARER_AUTH):
            raise NoBearerAuthorizationHeader()

        token = authorization_header[len(BEARER_AUTH) :].strip()

        try:
            decoded = decode(
                token,
                self.settings.authjwt.public_key,
                issuer=self.settings.authjwt.issuer,
                audience=self.settings.authjwt.audiences,
                algorithms=[ALGORITHM],
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
    ) -> User:
        user = await self.can_perform_required(request, user_permissions)

        try:
            ressource = await self.ressource_service.find_by_id(
                RessourceId(ressource_id, user.organization_id)
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
    ) -> User:
        oauth_id = self.authentification_required(request).get("sub")

        try:
            user = await self.user_service.find_by_id(oauth_id)
        except RecordNotFound:
            raise PermissionMissing("Permission missing", reason="user not found")

        for permission in permissions:
            if not permission in user.permissions:
                raise PermissionMissing("Permission missing", reason=permission)

        return user

    def make_token(self, oauth_id: str) -> str:
        if self.settings.authjwt.private_key is None:
            raise Exception("Missing private key to generate the token")

        return encode(
            {
                "aud": self.settings.authjwt.audiences,
                "sub": oauth_id,
                "iss": self.settings.authjwt.issuer,
            },
            self.settings.authjwt.private_key,
            algorithm=ALGORITHM,
        )
