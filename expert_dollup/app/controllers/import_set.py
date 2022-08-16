from fastapi import APIRouter, Depends, File, UploadFile
from uuid import UUID
from typing import Type, Optional, Callable, Any, List, Awaitable, Dict
from expert_dollup.shared.starlette_injection import Inject, CanPerformRequired
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.app.handlers import ImportRessourceHandler


router = APIRouter()


@router.post("/ressources/imports{user_id}")
async def import_definitiown_set(
    ressource_batch_import: RessourceBatchImportDto,
    file: UploadFile = File(...),
    handler: ImportRessourceHandler = Depends(Inject(ImportRessourceHandler)),
    user=Depends(CanPerformRequired(["ressource:imports"])),
):
    await handler.handle(ressource_batch_import.user_id, file.file.readlines())
