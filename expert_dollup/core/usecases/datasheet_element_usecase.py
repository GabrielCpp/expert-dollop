from uuid import UUID
from typing import Awaitable
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import DatasheetElement
from expert_dollup.infra.services import DatasheetElementService
from expert_dollup.infra.validators.schema_validator import SchemaValidator


class DatasheetElementUseCase:
    def __init__(
        self,
        datasheet_element_service: DatasheetElementService,
        schema_validator: SchemaValidator,
    ):
        self.datasheet_element_service = datasheet_element_service
        self.schema_validator = schema_validator
