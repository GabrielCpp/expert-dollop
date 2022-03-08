from typing import Union
from decimal import Decimal
from uuid import UUID

PrimitiveWithNoneUnion = Union[bool, int, str, Decimal, None]
PrimitiveUnion = Union[bool, int, str, Decimal]
PrimitiveWithReferenceUnion = Union[bool, int, str, Decimal, UUID]
