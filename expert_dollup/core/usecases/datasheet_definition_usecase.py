from uuid import UUID, uuid4
from typing import List
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import DatasheetDefinition, Ressource
from expert_dollup.infra.services import DatasheetDefinitionService, RessourceService
from expert_dollup.infra.validators.schema_validator import SchemaValidator
from expert_dollup.infra.providers import WordProvider


class DatasheetDefinitionUseCase:
    def __init__(
        self,
        datasheet_definition_service: DatasheetDefinitionService,
        schema_validator: SchemaValidator,
        ressource_service: RessourceService,
        word_provider: WordProvider,
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.schema_validator = schema_validator
        self.ressource_service = ressource_service
        self.word_provider = word_provider

    async def find_by_id(self, id: UUID):
        return await self.datasheet_definition_service.find_by_id(id)

    async def add(self, domain: DatasheetDefinition) -> DatasheetDefinition:
        ressource = Ressource(
            id=domain.id, kind="datsheet_definition", owner_id=uuid4()
        )
        self.validate_datasheet(domain)
        await self.ressource_service.insert(ressource)
        await self.datasheet_definition_service.insert(domain)
        return domain

    async def update(
        self, datasheet_definition: DatasheetDefinition
    ) -> DatasheetDefinition:
        self.validate_datasheet(datasheet_definition)
        await self.datasheet_definition_service.update(datasheet_definition)
        return await self.datasheet_definition_service.find_by_id(
            datasheet_definition.id
        )

    async def delete_by_id(self, id: UUID) -> None:
        await self.datasheet_definition_service.delete_by_id(id)

    def validate_datasheet(self, datasheet_definition: DatasheetDefinition):
        for name, schema in datasheet_definition.properties.items():
            if not self.schema_validator.is_valid_schema(schema.value_validator):
                raise ValidationError.for_field(f"properties.{name}", "Invalid schema")
