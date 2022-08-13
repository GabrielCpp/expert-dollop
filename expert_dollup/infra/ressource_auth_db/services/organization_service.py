from expert_dollup.core.domains import Organization
from expert_dollup.shared.database_services import CollectionServiceProxy
from ..daos import OrganizationDao


class OrganizationService(CollectionServiceProxy[Organization]):
    class Meta:
        dao = OrganizationDao
        domain = Organization
