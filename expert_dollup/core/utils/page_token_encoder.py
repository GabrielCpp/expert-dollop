from datetime import datetime
from uuid import UUID


def encode_date_with_uuid(date: datetime, id: UUID) -> str:
    return date.strftime("%Y%m%d%H%M%S") + id.hex
