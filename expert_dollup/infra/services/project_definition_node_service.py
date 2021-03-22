from typing import Awaitable, List, AsyncGenerator, Optional
from uuid import UUID
from sqlalchemy import select, text, bindparam, String, and_, or_, desc
from sqlalchemy.sql.expression import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects import postgresql
from expert_dollup.shared.database_services import (
    BaseCrudTableService,
    Page,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import (
    ProjectDefinitionContainerNode,
    ProjectDefinitionContainerNodeFilter,
)
from expert_dollup.infra.path_transform import join_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    project_definition_node_table,
    ProjectDefinitionContainerNodeDao,
)


DELETE_BY_MIXED_PATH = text(
    f"DELETE FROM {project_definition_node_table.name} WHERE mixed_paths <@ :element"
)


class ProjectDefinitionContainerNodeService(
    BaseCrudTableService[ProjectDefinitionContainerNode]
):
    class Meta:
        table = project_definition_node_table
        dao = ProjectDefinitionContainerNodeDao
        domain = ProjectDefinitionContainerNode
        table_filter_type = ProjectDefinitionContainerNodeFilter
        paginator = IdStampedDateCursorEncoder.for_fields("creation_date_utc", "name")

    async def has_path(self, path: List[UUID]) -> Awaitable[bool]:
        if len(path) == 0:
            return True

        parent_id = path[-1]
        parent_path = join_uuid_path(path[0:-1])
        query = select([self.table_id]).where(
            and_(self._table.c.path == parent_path, self._table.c.id == parent_id)
        )
        value = await self._database.fetch_one(query=query)

        return not value is None

    async def delete_child_of(self, id: UUID) -> Awaitable:
        query = self._table.select().where(self.table_id == id)
        value = await self._database.fetch_one(query=query)

        if value is None:
            return

        value = ProjectDefinitionContainerNodeDao(**value)
        path_to_delete = "/".join([*value.path, str(value.id)])
        sql = DELETE_BY_MIXED_PATH.bindparams(
            bindparam(
                key="element", value=[path_to_delete], type_=ARRAY(String, dimensions=1)
            )
        )

        await self._database.execute(sql)

    async def find_children_tree(self, project_def_id: UUID, path: List[UUID]):
        path_filter = join_uuid_path(path)
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_def_id == project_def_id,
                    self._table.c.mixed_paths.op("@>")([path_filter]),
                )
            )
            .order_by(desc(func.length(self._table.c.path)))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_viewable_layers(
        self,
        root_section_id: Optional[UUID],
        sub_root_section_id: Optional[UUID],
        form_id: Optional[UUID],
    ):
        first_layer = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_def_id == project_def_id,
                    self._table.c.mixed_paths.op("@>")([path_filter]),
                )
            )
            .order_by(desc(func.length(self._table.c.path)))
        )

        records = await self._database.fetch_all(query=first_layer)