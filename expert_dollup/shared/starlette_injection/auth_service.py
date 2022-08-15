from abc import ABC, abstractmethod
from typing import Union, List, Dict, Any, TypeVar, Generic, Optional
from uuid import UUID
from starlette.requests import Request

User = TypeVar("User")


class AuthService(ABC, Generic[User]):
    @abstractmethod
    def authentification_optional(self, request: Request) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def authentification_required(self, request: Request) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def can_perform_on_required(
        self,
        request: Request,
        ressource_id: UUID,
        permissions: Union[str, List[str]],
        user_permissions: Union[str, List[str]] = [],
    ) -> User:
        pass

    @abstractmethod
    async def can_perform_required(
        self, request: Request, permissions: Union[str, List[str]]
    ) -> User:
        pass
