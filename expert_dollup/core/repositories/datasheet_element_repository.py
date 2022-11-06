from abc import abstractmethod
from uuid import UUID
from typing import Optional, List, Dict, Union
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *


class DatasheetElementRepository(Repository[DatasheetElement]):
    @abstractmethod
    async def update_values(
        self,
        datasheet_id: UUID,
        datasheet_element_id: UUID,
        attributes: List[Attribute],
    ) -> None:
        pass
