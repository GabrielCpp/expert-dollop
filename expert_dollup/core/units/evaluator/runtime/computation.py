from typing import Union
from decimal import Decimal
from dataclasses import dataclass

PrimitiveWithNoneUnion = Union[bool, int, str, Decimal, None]


@dataclass
class Computation:
    value: PrimitiveWithNoneUnion = None
    details: str = ""
    index: int = 0

    def add(self, result, details) -> str:
        self.index = self.index + 1
        temp_name = f"temp{self.index}({result})"
        self.details = f"{self.details}\n{temp_name} = {details}"

        return temp_name

    def add_final(self, result, details) -> None:
        self.index = self.index + 1
        temp_name = f"\n<final_result, {result}>"
        self.details = f"{self.details}\n{temp_name} = {details}"
