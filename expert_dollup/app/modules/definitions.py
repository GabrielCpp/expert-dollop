from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.infra.ressource_auth_db import *

expert_dollup_metadatas = [
    RepositoryMetadata(dao=AggregateCollectionDao, domain=AggregateCollection),
    RepositoryMetadata(dao=AggregateDao, domain=Aggregate),
    RepositoryMetadata(dao=DatasheetElementDao, domain=DatasheetElement),
    RepositoryMetadata(dao=DatasheetDao, domain=Datasheet),
    RepositoryMetadata(dao=DistributableItemDao, domain=DistributableItem),
    RepositoryMetadata(dao=ProjectDefinitionFormulaDao, domain=Formula),
    RepositoryMetadata(dao=MeasureUnitDao, domain=MeasureUnit),
    RepositoryMetadata(dao=ProjectDefinitionNodeDao, domain=ProjectDefinitionNode),
    RepositoryMetadata(
        dao=Union[ProjectDefinitionNodeDao, ProjectDefinitionFormulaDao],
        domain=Union[ProjectDefinitionNode, Formula],
    ),
    RepositoryMetadata(dao=ProjectDefinitionDao, domain=ProjectDefinition),
    RepositoryMetadata(dao=ProjectNodeMetaDao, domain=ProjectNodeMeta),
    RepositoryMetadata(dao=ProjectNodeDao, domain=ProjectNode),
    RepositoryMetadata(dao=ProjectDao, domain=ProjectDetails),
    RepositoryMetadata(dao=ReportDefinitionDao, domain=ReportDefinition),
    RepositoryMetadata(dao=TranslationDao, domain=Translation),
]
auth_metadatas = [
    RepositoryMetadata(dao=OrganizationDao, domain=Organization),
    RepositoryMetadata(dao=RessourceDao, domain=Ressource),
    RepositoryMetadata(dao=UserDao, domain=User),
]
paginations = [
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("id"),
        for_domain=DatasheetElement,
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""),
        for_domain=Datasheet,
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""), for_domain=Formula
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""),
        for_domain=ProjectDefinitionNode,
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""),
        for_domain=ProjectDefinition,
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""),
        for_domain=ProjectDetails,
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""),
        for_domain=ReportDefinition,
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("id"), for_domain=Translation
    ),
    PaginationDetails(
        default_page_encoder=FieldTokenEncoder("name", str, str, ""),
        for_domain=Union[ProjectDefinitionNode, Formula],
    ),
]
