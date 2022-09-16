from abc import abstractmethod
from uuid import UUID
from typing import Optional, List, Dict, Union
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *


class DefinitionNodeFormulaRepository(
    Repository[Union[ProjectDefinitionNode, Formula]]
):
    @abstractmethod
    def make_node_query(self, definition_id: UUID, name: str) -> QueryBuilder:
        pass
