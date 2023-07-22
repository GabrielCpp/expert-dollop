from typing import List, Tuple, Literal, Optional, Any, Dict
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class QueryBuilder:
    selections: Optional[List[str]] = None
    limit_value: Optional[int] = None
    orders: Optional[List[Tuple[str, Literal["desc", "asc"]]]] = None
    wheres: List[List[Any]] = field(default_factory=list)
    constructs: Dict[str, List[Any]] = field(default_factory=lambda: defaultdict(list))

    @staticmethod
    def from_dcit(filters: dict) -> "QueryBuilder":
        return QueryBuilder(
            wheres=[[key, "==", value] for key, value in filters.items()]
        )

    def select(self, *names: List[str]) -> "QueryBuilder":
        if len(names) == 1 and names[0] == "*":
            self.selections = None

        elif len(names) >= 1:
            self.selections = names

        return self

    def limit(self, limit: int) -> "QueryBuilder":
        self.limit_value = limit
        return self

    def orderby(
        self, *orders: List[Tuple[str, Literal["desc", "asc"]]]
    ) -> "QueryBuilder":
        self.orders = orders
        return self

    def where(self, *ops) -> "QueryBuilder":
        self.wheres.append(ops)
        return self

    def construct(self, name, *ops) -> "QueryBuilder":
        self.constructs[name].extend(ops)
        return self

    def apply(self, builder: callable, *args, **kargs) -> "QueryBuilder":
        builder(self, *args, **kargs)
        return self

    def clone(self) -> "QueryBuilder":
        return deepcopy(self)
