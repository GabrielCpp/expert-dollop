from uuid import UUID, uuid4
from typing import Dict
from expert_dollup.core.domains.project_definition import ProjectDefinition
from expert_dollup.core.exceptions import ValidationError, InvalidUsageError
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import DatabaseContext
from expert_dollup.infra.validators.schema_validator import SchemaValidator
from expert_dollup.shared.starlette_injection import Clock


class DatasheetElementUseCase:
    def __init__(
        self,
        db_context: DatabaseContext,
        clock: Clock,
    ):
        self.db_context = db_context
        self.clock = clock

    async def find(
        self, datasheet_id: UUID, datasheet_element_id: UUID
    ) -> DatasheetElement:
        return await self.db_context.find_one_by(
            DatasheetElement,
            DatasheetElementFilter(
                id=datasheet_element_id,
                datasheet_id=datasheet_id,
            ),
        )

    async def count(
        self, datasheet_id: UUID, datasheet_element_id: UUID
    ) -> DatasheetElement:
        collection_size = await self.db_context.count(
            DatasheetElement,
            DatasheetElementFilter(
                datasheet_id=datasheet_id,
                element_def_id=datasheet_element_id,
            ),
        )
        return collection_size

    async def update(
        self,
        datasheet_id: UUID,
        datasheet_element_id: UUID,
        replacement: NewDatasheetElement,
    ) -> DatasheetElement:
        datasheet = await self.db_context.find_by_id(Datashet, datasheet_id)
        self._validate_datasheet_element_properties(replacement, datasheet)

        element = await self.find(datasheet_id, datasheet_element_id)
        new_element = DatasheetElement(
            id=element.id,
            datasheet_id=datasheet_id,
            aggregate_id=element.aggregate_id,
            ordinal=replacement.ordinal,
            attributes=replacement.attributes,
            original_datasheet_id=replacement.original_datasheet_id,
            original_owner_organization_id=replacement.original_owner_organization_id,
            creation_date_utc=element.creation_date_utc,
        )
        await self.db_context.upserts([new_element])
        return new_element

    async def add(
        self, datasheet_id: UUID, new_element: NewDatasheetElement, user: User
    ) -> DatasheetElement:
        datasheet = await self.db_context.find_by_id(Datasheet, datasheet_id)
        self._validate_datasheet_element_properties(new_element, datasheet)

        if not new_element.aggregate_id in datasheet.instances_schema:
            raise ValidationError.for_field(
                "aggregate_id", "Aggregate id does not exists for that datasheet"
            )

        aggregate_schema = datasheet.instances_schema[new_element.aggregate_id]
        if not aggregate_schema.is_collection:
            raise InvalidUsageError("Non collection element cannot be instanciated.")

        collection_size = await self.count(datasheet_id, datasheet_element_id)
        new_element = DatasheetElement(
            id=uuid4(),
            datasheet_id=datasheet_id,
            aggregate_id=new_element.aggregate_id,
            attributes=new_element.attributes,
            ordinal=new_element.ordinal or collection_size,
            original_owner_organization_id=user.organization_id,
            original_datasheet_id=datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )
        await self.datasheet_element_service.insert(new_element)

        return new_element

    async def batch_update_values(
        self, datasheet_id: UUID, updates: List[DatasheetElementUpdate]
    ) -> List[DatasheetElement]:
        datasheet = await self.db_context.find_by_id(Datasheet, datasheet_id)
        for update in updates:
            self._validate_datasheet_element_properties(update, datasheet)

        # TODO: finish the update

        self.db_context.upserts(DatsheetElement, domains)

    async def delete(self, datasheet_id: UUID, datasheet_element_id: UUID) -> None:
        datasheet = await self.db_context.find_by_id(Datasheet, datasheet_id)
        element = await self.find(datasheet_id, datasheet_element_id)
        aggregate_schema = datasheet.instances_schema[element.aggregate_id]

        if not aggregate_schema.is_collection:
            raise ValidationError.generic(
                "Non collection element cannot be instanciated."
            )

        collection_size = await self.count(datasheet_id, datasheet_element_id)
        if collection_size <= 1:
            raise ValidationError.generic("Cannot delete all items of collection")

        await self.db_context.delete_by_id(DatasheetElement, element_id)

    def _validate_datasheet_element_properties(
        self, replacement: DatasheetElementUpdate, datasheet: Datasheet
    ):
        replacement_names = set(attribute.name for attribute in replacement.attributes)
        expected_names = set(datasheet.attributes_schema.keys())

        missing_names = expected_names - replacement_names
        if len(missing_names) > 0:
            raise ValidationError.for_field(
                "attributes", "Missing field names", missing_names=missing_names
            )

        extra_names = replacement_names - expected_names
        if len(extra_names) > 0:
            raise ValidationError.for_field(
                "attributes", "Extra field names", extra_names=extra_names
            )

        instance_schema = datasheet.instances_schema[replacement.aggregate_id]

        for attribute in replacement.attributes:
            name = attribute.name
            default_instance = instance_schema.attributes_schema[name]

            if (
                default_instance.is_readonly
                and default_instance.value != attribute.value
            ):
                raise ValidationError.for_field(name, "Field is readonly")

            schema = datasheet.attributes_schema[name]
            # TODO: replace with propoer validation
