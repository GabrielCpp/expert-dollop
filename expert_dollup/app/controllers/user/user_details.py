from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from expert_dollup.core.domains import User
from expert_dollup.app.dtos import UserDto
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.shared.starlette_injection import (
    Inject,
    RequestHandler,
    MappingChain,
    AuthenticationRequired,
)

router = APIRouter()


@router.get("/user")
async def get_current_user(
    service=Depends(Inject(CollectionService[User])),
    mapper=Depends(Inject(Mapper)),
    user_dict=Depends(AuthenticationRequired()),
) -> UserDto:
    user = await service.find_by_id(user_dict.get("sub"))
    return mapper.map(user, UserDto)