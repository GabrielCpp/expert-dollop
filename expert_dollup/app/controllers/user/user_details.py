from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from expert_dollup.core.domains import User
from expert_dollup.app.dtos import UserDto
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import Repository
from expert_dollup.shared.database_services.exceptions import RecordNotFound
from expert_dollup.shared.starlette_injection import (
    Inject,
    RequestHandler,
    MappingChain,
    AuthenticationOptional,
)

router = APIRouter()


@router.get("/users/me")
async def get_current_user(
    service=Depends(Inject(Repository[User])),
    mapper=Depends(Inject(Mapper)),
    user_dict=Depends(AuthenticationOptional()),
) -> UserDto:
    if user_dict is None:
        return None

    try:
        user = await service.find_by_id(user_dict.get("sub"))

        return mapper.map(user, UserDto)
    except RecordNotFound:
        return None
