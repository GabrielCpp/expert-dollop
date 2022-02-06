from typing import List, Tuple, Literal
from collections import defaultdict
from .adapter_interfaces import QueryBuilder


class DbAgnotistQueryBuilder(QueryBuilder):
    def __init__(
        self,
        selections=None,
        max_records=None,
        orders=None,
        wheres=None,
        constructs=None,
    ):
        self._selections = selections
        self._max_records = max_records
        self._orders = orders
        self._wheres = wheres or []
        self._constructs = constructs or defaultdict(list)

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
        self._constructs[name].append(ops)
        return self

    def apply(self, builder: callable, *args, **kargs) -> QueryBuilder:
        builder(self, *args, **kargs)
        return self

    def clone(self) -> QueryBuilder:
        return DbAgnotistQueryBuilder(
            self._selections,
            self._max_records,
            self._orders,
            [*self._wheres],
            self._constructs,
        )
