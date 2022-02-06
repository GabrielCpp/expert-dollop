from typing import TypeVar, Optional, List
from uuid import UUID
from asyncio import gather
from expert_dollup.core.utils.ressource_permissions import get_ressource_kind
from expert_dollup.core.domains import Ressource, zero_uuid
from expert_dollup.core.queries import UserRessourcePaginator, UserRessourceQuery
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import (
    FieldTokenEncoder,
    Page,
    CollectionService,
    batch,
)


Domain = TypeVar("Domain")


class RessourceEngine(UserRessourcePaginator[Domain]):
    def __init__(
        self,
        user_service: CollectionService[Ressource],
        ressource_service: CollectionService[Ressource],
        mapper: Mapper,
        domain_service: CollectionService[Domain],
    ):
        self.user_service = user_service
        self.ressource_service = ressource_service
        self._mapper = mapper
        self._domain_service = domain_service
        self._default_page_encoder = FieldTokenEncoder(
            "date_ordering", str, str, ("0" * 12) + zero_uuid().hex
        )

    async def find_page(
        self,
        query: UserRessourceQuery,
        limit: int,
        next_page_token: Optional[str],
    ) -> Page[Domain]:
        kind = get_ressource_kind(self._domain_service.domain)
        builder = (
            self.ressource_service.get_builder()
            .where("user_id", "==", query.user_id)
            .where("kind", "==", kind)
            .where("permissions", "contain_one", f"{kind}:read")
        )
        scoped_builder = builder.clone()
        self._default_page_encoder.extend_query(scoped_builder, limit, next_page_token)
        results, total_count = await gather(
            self.ressource_service.find_by(scoped_builder),
            self.ressource_service.count(builder),
        )
        domains: List[Domain] = []

        new_next_page_token = self._default_page_encoder.default_token

        if len(results) > 0:
            last_result = results[-1]
            last_dao = self._mapper.map(last_result, self.ressource_service.dao)
            new_next_page_token = self._default_page_encoder.encode(last_dao)

            for results_batch in batch(results, 20):
                ids = [result.id for result in results_batch]
                query = self._domain_service.get_builder().where("id", "in", ids)
                domains_batch = await self._domain_service.find_by(query)
                domains_batch.sort(key=lambda o: ids.index(o.id))
                domains.extend(domains_batch)

        return Page(
            next_page_token=new_next_page_token,
            limit=limit,
            results=domains,
            total_count=total_count,
        )