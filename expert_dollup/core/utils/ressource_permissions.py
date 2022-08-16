from expert_dollup.core.domains import *
from typing import Type, Iterable, Set, List
from dataclasses import dataclass
from uuid import UUID
from itertools import chain
from enum import Enum


class Action(Enum):
    CAN_READ = "read"
    CAN_UPDATE = "update"
    CAN_CREATE = "create"
    CAN_DELETE = "delete"


@dataclass
class RessourceAuthorisation:
    kind: str
    actions: Set[str]


def set_of(*actions: str) -> frozenset:
    assert (
        all(isinstance(a, str) for a in actions) == True
    ), "All actions must be string"
    return frozenset(actions)


RESSOURCE_ACTIONS = frozenset(["read", "update", "create", "delete"])
RESSOURCE_KIND_BY_DOMAIN = {
    Ressource: RessourceAuthorisation("ressource", set_of("imports")),
    ProjectDetails: RessourceAuthorisation(
        "project", set_of(*RESSOURCE_ACTIONS, "clone")
    ),
    ProjectDefinition: RessourceAuthorisation("project_definition", RESSOURCE_ACTIONS),
    Translation: RessourceAuthorisation("translation", RESSOURCE_ACTIONS),
    Datasheet: RessourceAuthorisation("datasheet", set_of(*RESSOURCE_ACTIONS, "clone")),
}


def get_ressource_domain() -> List[Type]:
    return list(RESSOURCE_KIND_BY_DOMAIN.keys())


def get_ressource_kind(ressource: Type) -> str:
    return RESSOURCE_KIND_BY_DOMAIN[ressource].kind


def make_permission(ressource: Type, action: str) -> str:
    name = RESSOURCE_KIND_BY_DOMAIN[ressource].kind
    return f"{name}:{action}"


def make_permissions(ressource: Type, actions: Iterable[str]) -> List[str]:
    permissions = []

    for action in actions:
        permissions.append(make_permission(ressource, action))

    return permissions


def all_action() -> List[str]:
    return [r for r in RESSOURCE_ACTIONS]


def actions(*acts: Action) -> List[str]:
    return [action.value for action in acts]


def all_permisions() -> List[str]:
    permissions = []

    for ressource, ressource_authorisation in RESSOURCE_KIND_BY_DOMAIN.items():
        permissions.extend(make_permissions(ressource, ressource_authorisation.actions))

    return permissions


def make_ressource(
    kind: Type, target_ressource: RessourceProtocol, user: User
) -> Ressource:
    return Ressource(
        id=target_ressource.id,
        kind=RESSOURCE_KIND_BY_DOMAIN[kind].kind,
        organization_id=user.organization_id,
        permissions=make_permissions(kind, RESSOURCE_ACTIONS),
        name=target_ressource.name.split(),
        creation_date_utc=target_ressource.creation_date_utc,
    )
