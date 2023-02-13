from typing import List, Dict, Optional
from uuid import UUID
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.shared.database_services import *


class DefinitionNodeFormulaInternalRepository(RepositoryProxy):
    def __init__(
        self, repository: InternalRepository[Union[ProjectDefinitionNode, Formula]]
    ):
        RepositoryProxy.__init__(self, repository)
        self._repository = repository

    def make_node_query(self, definition_id: UUID, name: str) -> QueryBuilder:
        query = (
            QueryBuilder()
            .where("project_definition_id", "==", definition_id)
            .where("level", "==", FIELD_LEVEL)
        )

        if name != "":
            query.where("name", "startwiths", name)

        return query
