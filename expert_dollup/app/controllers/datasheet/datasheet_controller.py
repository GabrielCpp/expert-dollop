from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.domains import Datasheet, DatasheetElement
from expert_dollup.app.dtos import DatasheetDto, DatasheetElementDto
from expert_dollup.core.usecases import DatasheetUseCase

router = APIRouter()
