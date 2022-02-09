from abc import ABC, abstractclassmethod
from typing import Union, List
from uuid import UUID
from starlette.requests import Request


class AuthService(ABC):
    @abstractclassmethod
    def authentification_required(self, request: Request):
        pass

    @abstractclassmethod
    async def can_perform_on_required(
        self,
        request: Request,
        ressource_id: UUID,
        permissions: Union[str, List[str]],
        user_permissions: Union[str, List[str]] = [],
    ):
        pass

    @abstractclassmethod
    async def can_perform_required(
        self, request: Request, permissions: Union[str, List[str]]
    ):
        pass
