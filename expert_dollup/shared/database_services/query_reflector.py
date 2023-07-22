from functools import wraps
from typing import List, Dict, Callable, Type, Optional, Awaitable, Iterable
from typing_extensions import TypeAlias
from expert_dollup.shared.automapping import Mapper
from .adapter_interfaces import Repository, Domain

Executor: TypeAlias = Callable[
    [Mapper, Repository[Domain], Type], Awaitable[Iterable[Domain]]
]


class QueryReflector:
    def __init__(self):
        self.executors: Dict[Type, Executor] = {}

    def register_executor(self, q):
        def register(fn):
            self.executors[q] = fn
            return fn

        return register

    def register_child_of(self, parent_query):
        def register(child_query):
            async def call(mapper: Mapper, repository: Repository[Domain], query: Type):
                remapped = mapper.map(query, parent_query)
                handle = self.executors[parent_query]
                return await handle(repository, remapped)

            if parent_query in self.executors:
                self.executors[child_query] = call
                return child_query

            raise Exception("Parent querry not found.")

        return register

    def get_executor(self, obj):
        return self.executors.get(type(obj), None)


queries = QueryReflector()
