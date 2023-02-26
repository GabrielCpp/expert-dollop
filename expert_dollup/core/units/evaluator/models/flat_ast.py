from dataclasses import dataclass, field, asdict
from typing import Optional, Union, Dict, List
from decimal import Decimal


@dataclass
class AstNodeValue:
    number: Optional[Decimal] = None
    text: Optional[str] = None
    enabled: Optional[bool] = None


@dataclass
class FunctionParams:
    positional_names: List[str]


@dataclass
class AstNode:
    kind: str
    values: Dict[str, Union[AstNodeValue, FunctionParams, str]] = field(
        default_factory=dict
    )
    properties: Dict[str, int] = field(default_factory=dict)
    children: Dict[str, List[int]] = field(default_factory=dict)


@dataclass
class FlatAst:
    nodes: List[AstNode]
    root_index: int

    def dict(self) -> dict:
        return asdict(self)
