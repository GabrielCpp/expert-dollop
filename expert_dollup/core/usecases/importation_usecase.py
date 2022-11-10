from typing import List
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import DatabaseContext
from expert_dollup.core.utils.ressource_permissions import authorization_factory
from expert_dollup.core.domains import *
from .datasheet_usecase import DatasheetUseCase
from .project_definition_usecase import ProjectDefinitonUseCase
from .project_definition_node_usecase import ProjectDefinitionNodeUseCase
from .formula_usecase import FormulaUseCase
from .report_definition_usecase import ReportDefinitionUseCase
from .project_node_usecase import ProjectNodeUseCase


class ImportationUseCase:
    def __init__(
        self,
        mapper: Mapper,
        db_context: DatabaseContext,
        datasheet_use_case: DatasheetUseCase,
        project_definiton_use_case: ProjectDefinitonUseCase,
        project_definition_node_use_case: ProjectDefinitionNodeUseCase,
        formula_use_case: FormulaUseCase,
        report_definition_use_case: ReportDefinitionUseCase,
        project_node_use_case: ProjectNodeUseCase,
    ):
        self.mapper = mapper
        self.db_context = db_context
        self.datasheet_use_case = datasheet_use_case
        self.project_definiton_use_case = project_definiton_use_case
        self.project_definition_node_use_case = project_definition_node_use_case
        self.formula_use_case = formula_use_case
        self.report_definition_use_case = report_definition_use_case
        self.project_node_use_case = project_node_use_case

    async def import_datasheets(self, user: User, datasheets: List[Datasheet]):
        for datasheet in datasheets:
            await self.datasheet_use_case.add(datasheet, user)

    async def import_datasheet_elements(
        self, user: User, datasheet_elements: List[DatasheetElement]
    ):
        for datasheet_element in datasheet_elements:
            elements = await self.db_context.find_by(
                DatasheetElement,
                DatasheetElementFilter(
                    datasheet_id=datasheet_element.datasheet_id,
                    aggregate_id=datasheet_element.aggregate_id,
                    child_element_reference=datasheet_element.child_element_reference,
                ),
            )

            assert len(elements) == 0, f"element id exists {element} -> {elements}"
            await self.db_context.insert(DatasheetElement, datasheet_element)

    async def import_collections(
        self, user: User, collections: List[AggregateCollection]
    ):
        await self.db_context.insert_many(AggregateCollection, collections)

    async def import_translations(self, user: User, translations: List[Translation]):
        seen = {}
        dedup_translations = [
            seen.setdefault(
                (
                    translation.ressource_id,
                    translation.scope,
                    translation.locale,
                    translation.name,
                ),
                translation,
            )
            for translation in translations
            if not (
                translation.ressource_id,
                translation.scope,
                translation.locale,
                translation.name,
            )
            in seen
        ]

        await self.db_context.insert_many(Translation, dedup_translations)

    async def import_project_definitions(
        self, user: User, project_definitions: List[ProjectDefinition]
    ):
        for project_definition in project_definitions:
            await self.project_definiton_use_case.add(project_definition, user)

    async def import_project_definition_nodes(
        self, user: User, project_definition_nodes: List[ProjectDefinitionNode]
    ):
        for project_definition_node in project_definition_nodes:
            await self.project_definition_node_use_case.add(project_definition_node)

    async def import_formula_expressions(
        self, user: User, formula_expressions: List[FormulaExpression]
    ):
        await self.formula_use_case.add_many(formula_expressions)

    async def import_measure_units(
        self, user: User, project_definition_nodes: List[MeasureUnit]
    ):
        await self.db_context.insert_many(MeasureUnit, project_definition_nodes)

    async def import_report_definition(
        self, user: User, report_definitions: List[ReportDefinition]
    ):
        for report_definition in report_definitions:
            await self.report_definition_use_case.add(report_definition)

    async def import_project_nodes(self, user: User, project_nodes: List[ProjectNode]):
        await self.project_node_use_case.add_many(project_nodes)

    async def import_project_node_metas(
        self, user: User, project_node_metas: List[ProjectNodeMeta]
    ):
        await self.db_context.insert_many(ProjectNodeMeta, project_node_metas)

    async def import_projects_details(
        self, user: User, projects_details: List[ProjectDetails]
    ):
        for project_details in projects_details:
            ressource = authorization_factory.allow_access_to(
                project_details,
                user,
            )
            await self.db_context.insert(Ressource, ressource)
            await self.db_context.insert(ProjectDetails, project_details)
