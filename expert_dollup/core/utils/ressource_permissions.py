from expert_dollup.core.domains import *
from typing import Type, Iterable, Set, List, Mapping, Optional
from dataclasses import dataclass, field
from expert_dollup.core.exceptions import DetailedError
from collections import namedtuple

COMMON_ACTIONS: Set[str] = frozenset(["get", "list", "update", "create", "delete"])


def set_of(*actions: str) -> frozenset:
    assert (
        all(isinstance(a, str) for a in actions) == True
    ), "All actions must be string"
    return frozenset(actions)


def freeze_auth(*auths: "RessourceAuthorization"):
    return namedtuple(
        "RessourceAuthorizationMapping", [a.type.__name__ for a in auths]
    )(*auths)


@dataclass(frozen=True)
class RessourceAuthorization:
    type: Type
    kind: str
    permissions: Set[str]
    subressources: Mapping[str, "RessourceAuthorization"] = field(
        default_factory=namedtuple("Empty", [])
    )

    def ensure_permission_exists(self, permission: str) -> bool:
        if not permission in self.permissions:
            raise DetailedError(
                "Missing ressource permission",
                ressource=ressource,
                permission=permission,
                available_permission=self.permissions,
            )

        return True


@dataclass(frozen=True)
class AuthorizationFactory:
    authorizations: Mapping[str, RessourceAuthorization] = freeze_auth(
        RessourceAuthorization(Ressource, "ressource", set_of("imports")),
        RessourceAuthorization(
            ProjectDetails, "project", set_of(*COMMON_ACTIONS, "clone")
        ),
        RessourceAuthorization(ProjectDefinition, "project_definition", COMMON_ACTIONS),
        RessourceAuthorization(
            Datasheet, "datasheet", set_of(*COMMON_ACTIONS, "clone")
        ),
    )

    @property
    def ressource_types(self) -> List[Type]:
        return [a.type for a in self.authorizations]

    def get_ressource_details(self, ressource_type: Type) -> RessourceAuthorization:
        name = ressource_type.__name__

        if not name in self.authorizations:
            raise DetailedError(
                "Missing ressource type",
                ressource_type=ressource_type,
                available_ressource_types=self.ressource_types,
            )

        return self.authorizations[name]

    def get_ressource_kind(self, ressource_type: Type) -> str:
        return self.get_ressource_details(ressource_type).kind

    def build_permission_for(self, ressource_type: Type, permission: str) -> str:
        ressource_authorization = self.get_ressource_details(ressource_type)
        kind = ressource_authorization.kind

        ressource_authorization.ensure_permission_exists(permission)

        return f"{kind}:{permission}"

    def build_permissions_for(
        self, ressource_type: Type, permissions: Iterable[str]
    ) -> List[str]:
        ressource_authorization = self.get_ressource_details(ressource_type)
        kind = ressource_authorization.kind

        return [
            f"{kind}:{permission}"
            for permission in permissions
            if ressource_authorization.ensure_permission_exists(permission)
        ]

    def all_permissions_for(self, ressource_type: Type) -> List[str]:
        ressource_authorization = self.get_ressource_details(ressource_type)
        kind = ressource_authorization.kind

        return [
            f"{kind}:{permission}" for permission in ressource_authorization.permissions
        ]

    def all_permissions_for_each(self, *ressource_types: Type) -> List[str]:
        permissions = []

        for ressource_type in ressource_types:
            permissions.extend(self.all_permissions_for(ressource_type))

        return permissions

    def build_super_user_permisions(self) -> List[str]:
        permissions = []

        for a in self.authorizations:
            permissions.extend(self.all_permissions_for(a.type))

        return permissions

    def allow_access_to(
        self,
        target_ressource: RessourceProtocol,
        user: User,
        permissions: Optional[List[str]] = None,
    ) -> Ressource:
        ressource_type = type(target_ressource)
        return Ressource(
            id=target_ressource.id,
            kind=self.get_ressource_details(ressource_type).kind,
            organization_id=user.organization_id,
            permissions=self.all_permissions_for(ressource_type)
            if permissions is None
            else self.build_permissions_for(ressource_type, permissions),
            name=target_ressource.name.split(),
            creation_date_utc=target_ressource.creation_date_utc,
        )


authorization_factory = AuthorizationFactory()
