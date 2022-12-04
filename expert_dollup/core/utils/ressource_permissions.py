from expert_dollup.core.domains import *
from typing import Type, Iterable, Set, List, Dict, Optional
from dataclasses import dataclass, field
from uuid import UUID
from itertools import chain
from frozendict import frozendict
from expert_dollup.core.exceptions import DetailedError

COMMON_ACTIONS: Set[str] = frozenset(["get", "list", "update", "create", "delete"])


def set_of(*actions: str) -> frozenset:
    assert (
        all(isinstance(a, str) for a in actions) == True
    ), "All actions must be string"
    return frozenset(actions)


@dataclass(frozen=True)
class RessourceAuthorization:
    kind: str
    permissions: Set[str]
    subressources: Dict[Type, "RessourceAuthorization"] = field(
        default_factory=frozendict
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
    authorizations: Dict[Type, RessourceAuthorization] = frozendict(
        {
            Ressource: RessourceAuthorization("ressource", set_of("imports")),
            ProjectDetails: RessourceAuthorization(
                "project", set_of(*COMMON_ACTIONS, "clone")
            ),
            ProjectDefinition: RessourceAuthorization(
                "project_definition", COMMON_ACTIONS
            ),
            Datasheet: RessourceAuthorization(
                "datasheet", set_of(*COMMON_ACTIONS, "clone")
            ),
        }
    )

    @property
    def ressource_types(self) -> List[Type]:
        return list(self.authorizations.keys())

    def get_ressource_details(self, ressource_type: Type) -> RessourceAuthorization:
        if not ressource_type in self.authorizations:
            raise DetailedError(
                "Missing ressource type",
                ressource_type=ressource_type,
                available_ressource_types=self.ressource_types,
            )

        return self.authorizations[ressource_type]

    def get_ressource_kind(self, ressource_type: Type) -> str:
        return self.get_ressource_details(ressource_type).kind

    def build_permission_for(self, ressource_type: Type, permission: str) -> str:
        ressource_authorization = self.get_ressource_details(ressource_type)
        kind = ressource_authorization.kind

        ressource_authorization.ensure_permission_exists(permission)

        return f"{kind}:{permission}"

    def build_permissions_for(
        self, ressource: Type, permissions: Iterable[str]
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

        for ressource_type in self.authorizations.keys():
            permissions.extend(self.all_permissions_for(ressource_type))

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
