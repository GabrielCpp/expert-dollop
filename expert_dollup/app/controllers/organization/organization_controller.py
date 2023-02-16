from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.core.usecases import OrganizationUseCase
from expert_dollup.shared.starlette_injection import (
    Inject,
    RequestHandler,
    MappingChain,
    CanPerformOnRequired,
    AuthenticationRequired,
    Inject,
)
from expert_dollup.shared.database_services import Repository
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/organizations/{organization_id}")
async def get_organization_by_id(
    organization_id: UUID,
    service: Repository[Organization] = Depends(Inject(Repository[Organization])),
    handler=Depends(Inject(RequestHandler)),
    jwt_dict: dict = Depends(AuthenticationRequired()),
):
    return await handler.handle(
        service.find,
        organization_id,
        MappingChain(out_dto=OrganizationDto),
    )


@router.post("/organizations")
async def create_single_user_organization(
    single_user_organization: NewSingleUserOrganizationDto,
    usecase: OrganizationUseCase = Depends(Inject(OrganizationUseCase)),
    handler=Depends(Inject(RequestHandler)),
    jwt_dict: dict = Depends(AuthenticationRequired()),
):
    return await handler.forward(
        usecase.setup_organization,
        dict(
            email=single_user_organization.email,
            organization_name=single_user_organization.organization_name,
            oauth_id=jwt_dict["sub"],
        ),
        MappingChain(out_dto=UserDto),
    )
