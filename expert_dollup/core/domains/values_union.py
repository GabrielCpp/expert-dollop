from typing import Union
from decimal import Decimal

PrimitiveWithNoneUnion = Union[bool, int, str, Decimal, None]
PrimitiveUnion = Union[bool, int, str, Decimal]