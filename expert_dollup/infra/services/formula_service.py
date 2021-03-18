import jsonpickle
from sqlalchemy import select, join, and_, desc, or_, text
from sqlalchemy.sql.expression import func, select, alias
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Awaitable, Dict
from collections import defaultdict
from uuid import UUID
from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.core.domains import Formula, FormulaDetails, FormulaNode
from expert_dollup.infra.path_transform import split_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    ProjectDefinitionFormulaDao,
    project_definition_formula_table,
    project_definition_formula_dependency_table,
    project_definition_formula_container_dependency_table,
    project_definition_container_table,
)


class FormulaService(BaseCrudTableService[Formula]):
    class Meta:
        table = project_definition_formula_table
        dao = ProjectDefinitionFormulaDao
        domain = Formula
        table_filter_type = None

    async def get_formulas_by_name(
        self, names: List[str]
    ) -> Awaitable[Dict[str, UUID]]:
        query = select(
            [
                project_definition_formula_table.c.id,
                project_definition_formula_table.c.name,
            ]
        ).where(project_definition_formula_table.c.name.in_(names))

        records = await self._database.fetch_all(query=query)
        return {record.get("name"): record.get("id") for record in records}

    async def get_fields_by_name(self, names: List[str]) -> Awaitable[Dict[str, UUID]]:
        query = select(
            [
                project_definition_container_table.c.id,
                project_definition_container_table.c.name,
            ]
        ).where(project_definition_container_table.c.name.in_(names))

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

        query = project_definition_formula_container_dependency_table.delete().where(
            project_definition_formula_container_dependency_table.c.formula_id
            == formula_details.formula.id
        )

        await self._database.execute(query=query)

        query = pg_insert(
            project_definition_formula_container_dependency_table,
            [
                {
                    "formula_id": formula_details.formula.id,
                    "depend_on_container_id": field_dependency,
                    "project_def_id": formula_details.formula.project_def_id,
                }
                for field_dependency in formula_details.field_dependencies.values()
            ],
        )

        if len(formula_details.field_dependencies) > 0:
            await self._database.execute(query=query)

        formula_dao = self._mapper.map(formula_details.formula, self._dao, self._domain)

        query = (
            self._table.update()
            .where(self._table.c.id == formula_details.formula.id)
            .values({"generated_ast": formula_dao.generated_ast})
        )

        await self._database.execute(query=query)

    async def get_all_project_formula_ast(
        self, project_definition_id: UUID
    ) -> Awaitable[List[FormulaNode]]:
        join_definition = self._table.join(
            project_definition_container_table,
            and_(
                project_definition_container_table.c.id
                == self._table.c.attached_to_type_id,
                project_definition_container_table.c.project_def_id
                == project_definition_id,
            ),
        )

        query = (
            select(
                [
                    self._table.c.name,
                    self._table.c.generated_ast,
                    self._table.c.id.label("formula_id"),
                    project_definition_container_table.c.path,
                    project_definition_container_table.c.id,
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
            [project_definition_formula_container_dependency_table]
        ).where(
            project_definition_formula_container_dependency_table.c.project_def_id
            == project_definition_id
        )

        field_dependency_records = await self._database.fetch_all(
            query=query_field_dependencies
        )

        dependencies = defaultdict(list)
        for element in field_dependency_records:
            dependencies[element.get("formula_id")].append(
                element.get("depend_on_container_id")
            )

        for element in query_formula_dependency_records:
            dependencies[element.get("formula_id")].append(
                element.get("depend_on_formula_id")
            )

        records = await self._database.fetch_all(query=query)

        return [
            FormulaNode(
                id=record.get("id"),
                name=record.get("name"),
                path=split_uuid_path(record.get("path")),
                expression=jsonpickle.decode(record.get("generated_ast")),
                dependencies=dependencies[record.get("formula_id")],
                formula_id=record.get("formula_id"),
            )
            for record in records
        ]
