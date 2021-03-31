import base64
import json
import dateutil.parser
from typing import Awaitable, Optional, Tuple, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import desc, select, and_


class IdStampedDateCursorEncoder:
    @staticmethod
    def for_fields(
        id_field_name: str,
        build_id_field=UUID,
        extract_field_id=str,
    ):
        return lambda table: IdStampedDateCursorEncoder(
            table, id_field_name, build_id_field, extract_field_id
        )

    def __init__(
        self,
        table,
        id_field_name: str,
        build_id_field: callable,
        extract_field_id: callable,
    ):
        self.table = table
        self.id_field_name = id_field_name
        self._build_id_field = build_id_field
        self._extract_field_id = extract_field_id

    def encode_dao(self, dao: BaseModel):
        dao_id = getattr(dao, self.id_field_name)
        return self._encode(dao_id)

    def encode_record(self, record):
        record_id = record[self.id_field_name]
        return self._encode(record_id)

    def build_query(self, filter_condition, limit: int, next_page_token: Optional[str]):
        id_column = getattr(self.table.c, self.id_field_name)

        if not next_page_token is None:
            from_id = self._decode(next_page_token)
            filter_condition = and_(
                filter_condition,
                id_column < from_id,
            )

        query = (
            self.table.select()
            .where(filter_condition)
            .order_by(desc(id_column))
            .limit(limit)
        )

        return query

    def _encode(self, id: Any):
        id_str = self._extract_field_id(id)
        token = base64.urlsafe_b64encode(id_str.encode("ascii"))
        return token

    def _decode(self, cursor: str) -> Any:
        id_field_str = base64.urlsafe_b64decode(cursor.encode("ascii"))
        id_field = self._build_id_field(id_field_str.decode("ascii"))
        return id_field
