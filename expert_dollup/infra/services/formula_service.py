from expert_dollup.core.domains.formula import FormulaFilter
import ast
from sqlalchemy import select, join, and_, desc, or_, text
from sqlalchemy.sql.expression import func, select, alias, tuple_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Awaitable, Dict
from collections import defaultdict
from uuid import UUID
from expert_dollup.shared.database_services import (
    PostgresTableService,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import (
    Formula,
    FormulaDetails,
    FormulaNode,
    FormulaPluckFilter,
)
from expert_dollup.core.utils.path_transform import split_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    ProjectDefinitionFormulaDao,
    project_definition_formula_table,
    project_definition_formula_dependency_table,
    project_definition_formula_node_dependency_table,
    project_definition_node_table,
    project_node_table,
)


class FormulaService(PostgresTableService[Formula]):
    class Meta:
        table = project_definition_formula_table
        dao = ProjectDefinitionFormulaDao
        domain = Formula
        table_filter_type = FormulaFilter
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")

    async def get_formulas_by_name(
        self, names: List[str]
    ) -> Awaitable[Dict[str, UUID]]:
        if len(names) == 0:
            return {}

        query = (
            self.get_builder()
            .select_fields("id", "name")
            .pluck(FormulaPluckFilter(names=names))
            .finalize()
        )
        records = await self.fetch_all_records(query)

        return {record.get("name"): record.get("id") for record in records}

    async def get_fields_by_name(self, names: List[str]) -> Awaitable[Dict[str, UUID]]:
        if len(names) == 0:
            return {}

        query = select(
            [
                project_definition_node_table.c.id,
                project_definition_node_table.c.name,
            ]
        ).where(project_definition_node_table.c.name.in_(tuple_(*names)))

        records = await self._database.fetch_all(query=query)
        return {record.get("name"): record.get("id") for record in records}

    async def patch_formula_graph(self, formula_details: FormulaDetails) -> Awaitable:
        query = project_definition_formula_dependency_table.delete().where(
            project_definition_formula_dependency_table.c.formula_id
            == formula_details.formula.id
        )

        await self._database.execute(query=query)

        query = pg_insert(
            project_definition_formula_dependency_table,
            [
                {
                    "formula_id": formula_details.formula.id,
                    "depend_on_formula_id": formula_dependency,
                    "project_def_id": formula_details.formula.project_def_id,
                }
                for formula_dependency in formula_details.formula_dependencies.values()
            ],
        )

        if len(formula_details.formula_dependencies) > 0:
            await self._database.execute(query=query)

        query = project_definition_formula_node_dependency_table.delete().where(
            project_definition_formula_node_dependency_table.c.formula_id
            == formula_details.formula.id
        )

        await self._database.execute(query=query)

        query = pg_insert(
            project_definition_formula_node_dependency_table,
            [
                {
                    "formula_id": formula_details.formula.id,
                    "depend_on_node_id": field_dependency,
                    "project_def_id": formula_details.formula.project_def_id,
                }
                for field_dependency in formula_details.field_dependencies.values()
            ],
        )

        if len(formula_details.field_dependencies) > 0:
            await self._database.execute(query=query)

    async def get_all_project_formula_ast(
        self, project_id: UUID, project_definition_id: UUID
    ) -> Awaitable[List[FormulaNode]]:
        join_definition = self._table.join(
            project_node_table,
            and_(
                project_node_table.c.type_id == self._table.c.attached_to_type_id,
                project_node_table.c.project_id == project_id,
            ),
        )

        query = (
            select(
                [
                    self._table.c.name,
                    self._table.c.expression,
                    self._table.c.id.label("formula_id"),
                    project_node_table.c.path,
                    project_node_table.c.id,
                    project_node_table.c.type_id,
                    project_node_table.c.type_path,
                ]
            )
            .select_from(join_definition)
            .where(self._table.c.project_def_id == project_definition_id)
        )

        query_formula_dependencies = select(
            [
                project_definition_formula_dependency_table.c.depend_on_formula_id,
                project_definition_formula_dependency_table.c.formula_id,
            ]
        ).where(
            project_definition_formula_dependency_table.c.project_def_id
            == project_definition_id
        )

        query_formula_dependency_records = await self._database.fetch_all(
            query=query_formula_dependencies
        )

        query_field_dependencies = select(
            [project_definition_formula_node_dependency_table]
        ).where(
            project_definition_formula_node_dependency_table.c.project_def_id
            == project_definition_id
        )

        field_dependency_records = await self._database.fetch_all(
            query=query_field_dependencies
        )

        dependencies = defaultdict(list)
        for element in field_dependency_records:
            dependencies[element.get("formula_id")].append(
                element.get("depend_on_node_id")
            )

        for element in query_formula_dependency_records:
            dependencies[element.get("formula_id")].append(
                element.get("depend_on_formula_id")
            )

        records = await self._database.fetch_all(query=query)

        return [
            FormulaNode(
                id=record.get("id"),
                expression=ast.parse(record.get("expression")),
                name=record.get("name"),
                path=split_uuid_path(record.get("path")),
                type_id=record.get("type_id"),
                type_path=split_uuid_path(record.get("type_path")),
                dependencies=dependencies[record.get("formula_id")],
                formula_id=record.get("formula_id"),
            )
            for record in records
        ]
