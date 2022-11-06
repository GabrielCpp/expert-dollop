from typing import List, Tuple, Literal, Optional, Any, Dict
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from .adapter_interfaces import QueryBuilder


@dataclass
class DbAgnotistQueryBuilder(QueryBuilder):
    _selections: Optional[List[str]] = None
    _max_records: Optional[int] = None
    _orders: Optional[List[Tuple[str, Literal["desc", "asc"]]]] = None
    _wheres: List[List[Any]] = field(default_factory=list)
    _constructs: Dict[str, List[Any]] = field(default_factory=lambda: defaultdict(list))

    def select(self, *names: List[str]) -> QueryBuilder:
        if len(names) == 1 and names[0] == "*":
            self._selections = None

        elif len(names) >= 1:
            self._selections = names

        return self

    def limit(self, limit: int) -> QueryBuilder:
        self._max_records = limit
        return self

    def orderby(
        self, *orders: List[Tuple[str, Literal["desc", "asc"]]]
    ) -> QueryBuilder:
        self._orders = orders
        return self

    def where(self, *ops) -> QueryBuilder:
        self._wheres.append(ops)
        return self

    def construct(self, name, *ops) -> QueryBuilder:
        self._constructs[name].extend(ops)
        return self

    def apply(self, builder: callable, *args, **kargs) -> QueryBuilder:
        builder(self, *args, **kargs)
        return self

    def clone(self) -> QueryBuilder:
        return deepcopy(self)
