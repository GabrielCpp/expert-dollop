from abc import abstractmethod
from uuid import UUID
from typing import Optional, List, Dict
from expert_dollup.shared.database_services import Repository
from expert_dollup.core.domains import Formula


class FormulaRepository(Repository[Formula]):
    @abstractmethod
    async def get_formulas_id_by_name(
        self, project_definition_id: UUID, names: Optional[List[str]] = None
    ) -> Dict[str, UUID]:
        pass
