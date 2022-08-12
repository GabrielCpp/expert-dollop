from uuid import UUID, uuid4
from typing import Dict
from expert_dollup.core.domains.project_definition import ProjectDefinition
from expert_dollup.core.exceptions import ValidationError, InvalidUsageError
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.infra.validators.schema_validator import SchemaValidator
from expert_dollup.shared.starlette_injection import Clock


class DatasheetElementUseCase:
    def __init__(
        self,
        datasheet_service: CollectionService[Datasheet],
        datasheet_element_service: CollectionService[DatasheetElement],
        schema_validator: SchemaValidator,
        datasheet_definition_element_service: CollectionService[
            DatasheetDefinitionElement
        ],
        ressource_service: CollectionService[Ressource],
        project_definition_service: CollectionService[ProjectDefinition],
        clock: Clock,
    ):
        self.datasheet_service = datasheet_service
        self.datasheet_element_service = datasheet_element_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.schema_validator = schema_validator
        self.project_definition_service = project_definition_service
        self.ressource_service = ressource_service
        self.clock = clock

    async def find_datasheet_element(self, id: DatasheetElementId) -> DatasheetElement:
        return await self.datasheet_element_service.find_by_id(id)

    async def update_datasheet_element_properties(
        self, id: DatasheetElementId, properties: Dict[str, PrimitiveUnion]
    ) -> DatasheetElement:
        datasheet: Datasheet = await self.datasheet_service.find_by_id(id.datasheet_id)
        project_definition: ProjectDefinition = (
            await self.project_definition_service.find_by_id(
                datasheet.project_definition_id
            )
        )
        element_definition: DatasheetDefinitionElement = (
            await self.datasheet_definition_element_service.find_by_id(
                id.element_def_id
            )
        )

        self._validate_datasheet_element_properties(
            properties, project_definition, element_definition
        )

        await self.datasheet_element_service.update(
            DatasheetElementValues(properties=properties),
            DatasheetElementFilter(
                datasheet_id=id.datasheet_id,
                element_def_id=id.element_def_id,
                child_element_reference=id.child_element_reference,
            ),
        )

        return await self.datasheet_element_service.find_by_id(id)

    async def add_collection_item(
        self,
        datasheet_id: UUID,
        element_def_id: UUID,
        properties: Dict[str, PrimitiveUnion],
    ) -> DatasheetElement:
        datasheet: Datasheet = await self.datasheet_service.find_by_id(datasheet_id)
        project_definition: ProjectDefinition = (
            await self.project_definition_service.find_by_id(
                datasheet.project_definition_id
            )
        )
        element_definition: DatasheetDefinitionElement = (
            await self.datasheet_definition_element_service.find_by_id(element_def_id)
        )

        if not element_definition.is_collection:
            raise InvalidUsageError("Non collection element cannot be instanciated.")

        self._validate_datasheet_element_properties(
            properties, project_definition, element_definition
        )

        datasheet_ressource = await self.ressource_service.find_one_by(
            RessourceFilter(id=datasheet_id)
        )
        new_element = DatasheetElement(
            datasheet_id=datasheet_id,
            element_def_id=element_def_id,
            child_element_reference=uuid4(),
            properties=properties,
            ordinal=1,  # TODO: find max
            original_owner_organization_id=datasheet_ressource.organization_id,
            original_datasheet_id=datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )
        await self.datasheet_element_service.insert(new_element)

        return new_element

    async def delete_element(self, element_id: DatasheetElementId) -> None:
        element_definition: DatasheetDefinitionElement = (
            await self.datasheet_definition_element_service.find_by_id(
                element_id.element_def_id
            )
        )

        if not element_definition.is_collection:
            raise InvalidUsageError("Non collection element cannot be instanciated.")

        collection_size = await self.datasheet_element_service.count(
            DatasheetElementFilter(
                datasheet_id=element_id.datasheet_id,
                element_def_id=element_id.element_def_id,
            )
        )

        if collection_size <= 1:
            raise InvalidUsageError("Cannot delete all items of collection")

        await self.datasheet_element_service.delete_by_id(element_id)

    def _validate_datasheet_element_properties(
        self,
        properties: Dict[str, PrimitiveUnion],
        project_definition: ProjectDefinition,
        element_definition: DatasheetDefinitionElement,
    ):
        for name, default_property in element_definition.default_properties.items():
            if name in properties:
                if default_property.is_readonly is True:
                    raise ValidationError.for_field(name, "Field is readonly")

                assert name in project_definition.properties
                property_schema = project_definition.properties[name].value_validator
                self.schema_validator.validate_instance_of(
                    property_schema, properties[name]
                )

            elif default_property.is_readonly is False:
                raise ValidationError.for_field(name, "Field is missing")

        for name in properties.keys():
            if not name in project_definition.properties:
                raise ValidationError.for_field(name, "Field does not exist")
