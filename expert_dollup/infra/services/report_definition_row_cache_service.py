from expert_dollup.infra.expert_dollup_db import ReportDefinitionRowCacheDao
from expert_dollup.core.domains import ReportDefinitionRowCache
from expert_dollup.shared.database_services import CollectionServiceProxy


class ReportDefinitionRowCacheService(CollectionServiceProxy[ReportDefinitionRowCache]):
    class Meta:
        dao = ReportDefinitionRowCacheDao
        domain = ReportDefinitionRowCache