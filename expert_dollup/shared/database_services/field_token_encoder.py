import base64
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel
from .adapter_interfaces import (
    QueryBuilder,
    WhereFilter,
    TokenEncoder,
)
from .page import Page


class FieldTokenEncoder(TokenEncoder):
    def __init__(
        self,
        id_field_name: str,
        build_id_field: callable = UUID,
        extract_field_id: callable = str,
        default_id: str = UUID("00000000-0000-0000-0000-000000000000"),
    ):
        self.id_field_name = id_field_name
        self._build_id_field = build_id_field
        self._extract_field_id = extract_field_id
        self.default_token = self.encode_field(default_id)

    def extend_query(
        self, builder: WhereFilter, limit: int, next_page_token: Optional[str]
    ) -> QueryBuilder:
        id_column = self.id_field_name

        if not next_page_token is None:
            from_id = self.decode(next_page_token)
            builder.where(id_column, "<", from_id)

        return builder.orderby((id_column, "desc")).limit(limit)

    def encode(self, dao: BaseModel):
        dao_id = getattr(dao, self.id_field_name)
        return self.encode_field(dao_id)

    def encode_field(self, dao_id: str):
        id_str = self._extract_field_id(dao_id)
        token = base64.urlsafe_b64encode(id_str.encode("utf8"))
        return token.decode("utf8")

    def decode(self, cursor: str) -> Any:
        id_field_str = base64.urlsafe_b64decode(cursor.encode("utf8"))
        id_field = self._build_id_field(id_field_str.decode("utf8"))
        return id_field
