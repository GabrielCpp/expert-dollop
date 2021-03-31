import base64
import json
import dateutil.parser
from typing import Awaitable, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import desc, select, and_
from urllib.parse import unquote, quote


class IdStampedDateCursorEncoder:
    @staticmethod
    def encode(date: datetime, id: UUID):
        date_str = date.isoformat()
        id_str = str(id)
        cursor = json.dumps({"date": date_str, "id": id_str}, sort_keys=True)

        return quote(base64.urlsafe_b64encode(cursor.encode("utf8")))

    @staticmethod
    def decode(cursor: str, build_id_field) -> Tuple[datetime, UUID]:
        cursor_json_str = base64.urlsafe_b64decode(unquote(cursor).encode("utf8"))
        cursor_dict = json.loads(cursor_json_str)
        date = dateutil.parser.isoparse(cursor_dict["date"])
        id = build_id_field(cursor_dict["id"])
        return (date, id)

    @staticmethod
    def for_fields(date_field_name, id_field_name, build_id_field=UUID):
        return lambda table: IdStampedDateCursorEncoder(
            table, date_field_name, id_field_name, build_id_field
        )

    def __init__(self, table, date_field_name, id_field_name, build_id_field):
        self.table = table
        self.date_field_name = date_field_name
        self.id_field_name = id_field_name
        self._build_id_field = build_id_field

    def encode_dao(self, dao):
        dao_id = getattr(dao, self.id_field_name)
        dao_date = getattr(dao, self.date_field_name)
        return IdStampedDateCursorEncoder.encode(dao_date, dao_id)

    def encode_record(self, record):
        record_id = record[self.id_field_name]
        record_date = record[self.date_field_name]
        return IdStampedDateCursorEncoder.encode(record_date, record_id)

    def build_query(self, filter_condition, limit: int, next_page_token: Optional[str]):
        date_column = getattr(self.table.c, self.date_field_name)
        id_column = getattr(self.table.c, self.id_field_name)

        if not next_page_token is None:
            from_date, from_id = IdStampedDateCursorEncoder.decode(
                next_page_token, self._build_id_field
            )

            filter_condition = and_(
                filter_condition,
                date_column >= from_date,
                id_column > from_id,
            )

        query = (
            self.table.select()
            .where(filter_condition)
            .order_by(
                desc(date_column),
                desc(id_column),
            )
            .limit(limit)
        )

        return query
