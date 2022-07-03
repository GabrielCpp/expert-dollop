from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.core.usecases import OrganisationUseCase
from expert_dollup.shared.starlette_injection import (
    Inject,
    RequestHandler,
    MappingChain,
    CanPerformOnRequired,
    AuthenticationRequired,
    Inject,
)
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.post("/organisations")
async def create_single_user_organisation(
    single_user_organisation: NewSingleUserOrganisationDto,
    usecase: OrganisationUseCase = Depends(Inject(OrganisationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    jwt_dict: dict = Depends(AuthenticationRequired()),
):
    return await handler.forward(
        usecase.setup_organisation,
        dict(
            email=single_user_organisation.email,
            organisation_name=single_user_organisation.organisation_name,
            oauth_id=jwt_dict["sub"],
        ),
        MappingChain(out_dto=UserDto),
    )