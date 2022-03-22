from expert_dollup.core.domains import Organisation
from expert_dollup.shared.database_services import CollectionServiceProxy
from ..daos import OrganisationDao


class OrganisationService(CollectionServiceProxy[Organisation]):
    class Meta:
        dao = OrganisationDao
        domain = Organisation
