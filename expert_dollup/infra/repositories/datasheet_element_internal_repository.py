from typing import List, Dict, Optional
from uuid import UUID
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.shared.database_services import *
from expert_dollup.shared.automapping import Mapper
from expert_dollup.infra.mappings import primitive_with_reference_union_dao_mappings


class DatasheetElementInternalRepository(RepositoryProxy):
    def __init__(
        self, repository: InternalRepository[DatasheetElement], mapper: Mapper
    ):
        RepositoryProxy.__init__(self, repository)
        self._repository = repository
        self._mapper = mapper

    async def update_values(
        self,
        datasheet_id: UUID,
        datasheet_element_id: UUID,
        attributes: List[Attribute],
    ) -> DatasheetElement:
        builder = self._repository.get_builder().construct(
            "find_one_and_update",
            {
                "_id": str(datasheet_element_id),
            },
            {
                "$set": {
                    f"attributes.{attribute.name}": self._repository._query_compiler.simplify(
                        self._mapper.map(attribute, AttributeDao)
                    )
                    for attribute in attributes
                }
            },
        )

        result = await self._repository.apply_construct(builder)
        return result
