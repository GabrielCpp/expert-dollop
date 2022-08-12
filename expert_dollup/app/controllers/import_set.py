from fastapi import APIRouter, Depends, File, UploadFile
from uuid import UUID
from typing import Type, Optional, Callable, Any, List, Awaitable, Dict
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.app.handlers import ImportRessourceHandler


router = APIRouter()


@router.post("/import/{user_id}")
async def import_definitiown_set(
    user_id: UUID,
    file: UploadFile = File(...),
    handler: ImportRessourceHandler = Depends(Inject(ImportRessourceHandler)),
):
    await handler.handle(user_id, file.file.readlines())
