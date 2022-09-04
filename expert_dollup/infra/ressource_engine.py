from typing import TypeVar, Optional, List, Union
from asyncio import gather
from expert_dollup.core.utils import encode_date_with_uuid, authorization_factory
from expert_dollup.core.domains import Ressource, RessourceProtocol
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import (
    FieldTokenEncoder,
    Page,
    InternalRepository,
    batch,
    UserRessourcePaginator,
    UserRessourceQuery,
)


Domain = TypeVar("Domain", bound=RessourceProtocol)


class RessourceEngine(UserRessourcePaginator[Domain]):
    def __init__(
        self,
        user_service: InternalRepository[Ressource],
        ressource_service: InternalRepository[Ressource],
        mapper: Mapper,
        domain_service: InternalRepository[Domain],
    ):
        self.user_service = user_service
        self.ressource_service = ressource_service
        self._mapper = mapper
        self._domain_service = domain_service
        self._page_encoder = FieldTokenEncoder(
            "date_ordering", str, str, ("0" * 12) + ("0" * 32)
        )
        self._domain_get_permission = authorization_factory.build_permission_for(
            self._domain_service.domain, "get"
        )
        self._kind = authorization_factory.get_ressource_kind(
            self._domain_service.domain
        )

    async def find_page(
        self,
        query: UserRessourceQuery,
        limit: int,
        next_page_token: Optional[str],
    ) -> Page[Domain]:
        builder = (
            self.ressource_service.get_builder()
            .where("organization_id", "==", query.organization_id)
            .where("kind", "==", self._kind)
            .where("permissions", "contain_one", self._domain_get_permission)
        )
        scoped_builder = builder.clone()
        self._page_encoder.extend_query(scoped_builder, limit, next_page_token)
        results, total_count = await gather(
            self.ressource_service.find_by(scoped_builder),
            self.ressource_service.count(builder),
        )
        domains: List[Domain] = []

        new_next_page_token = self._page_encoder.default_token

        if len(results) > 0:
            last_result = results[-1]
            new_next_page_token = self.make_record_token(last_result)

            for results_batch in batch(results, self._domain_service.batch_size):
                ids = [result.id for result in results_batch]
                query_builder = self._domain_service.get_builder().where(
                    "id", "in", ids
                )
                domains_batch = await self._domain_service.find_by(query_builder)
                domains_batch.sort(key=lambda o: ids.index(o.id))
                domains.extend(domains_batch)

        return Page(
            next_page_token=new_next_page_token,
            limit=limit,
            results=domains,
            total_count=total_count,
        )

    def make_record_token(self, domain: Union[Domain, Ressource]) -> str:
        token = encode_date_with_uuid(domain.creation_date_utc, domain.id)
        new_next_page_token = self._page_encoder.encode_field(token)
        return new_next_page_token
