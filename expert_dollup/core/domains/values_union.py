from typing import Union
from typing_extensions import TypeAlias
from decimal import Decimal
from uuid import UUID

PrimitiveWithNoneUnion: TypeAlias = Union[bool, int, str, Decimal, None]
PrimitiveUnion: TypeAlias = Union[bool, int, str, Decimal]
PrimitiveWithReferenceUnion: TypeAlias = Union[bool, int, str, Decimal, UUID]
