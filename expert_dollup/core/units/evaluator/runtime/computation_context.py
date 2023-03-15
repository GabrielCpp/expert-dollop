import ast
from typing import Dict, List
from dataclasses import dataclass
from typing_extensions import TypeAlias
from .types import AnyCallable
from .computation import Computation

LexicalScope: TypeAlias = Dict[str, Computation]


@dataclass
class ComputationContext:
    global_functions: Dict[str, AnyCallable]
    lexical_scopes: List[LexicalScope]
    calc: Computation
    nodes: List[dict]

    def append_scope(self, new_vars: dict) -> LexicalScope:
        if len(self.lexical_scopes) == 0:
            raise AstRuntimeError("No lexical scope in the context")

        lexical_scope = self.lexical_scopes[-1]
        new_lexical_scope = dict(lexical_scope)
        new_lexical_scope.update(new_vars)
        self.lexical_scopes.append(new_lexical_scope)

        return new_lexical_scope

    def assign(self, target, value) -> None:
        if len(self.lexical_scopes) == 0:
            raise AstRuntimeError("No lexical scope in the context")

        lexical_scope = self.lexical_scopes[-1]
        lexical_scope[target] = value

    def pop_scope(self) -> None:
        self.lexical_scopes.pop()

    def is_kind(self, node: dict, kind: str) -> bool:
        return node["kind"] == kind

    def get_function(self, name: str) -> AnyCallable:
        return self.global_functions[name]

    def has_property(self, node: dict, name: str) -> bool:
        return name in node["properties"]

    def get_property(self, node: dict, name: str) -> dict:
        return self.nodes[node["properties"][name]]

    def has_children(self, node, name) -> bool:
        return name in node["children"]

    def get_children(self, node, name) -> list:
        return [self.nodes[c] for c in node["children"][name]]

    def get_name(self, name: str) -> Computation:
        value = self.global_functions.get(name, None)

        if not value is None:
            return Computation(value=value)

        if len(self.lexical_scopes) == 0:
            raise AstRuntimeError("No lexical scope in the context")

        lexical_scope = self.lexical_scopes[-1]

        if not name in lexical_scope:
            raise AstRuntimeError(
                "Lexical scope is missing a name",
                names=list(lexical_scope.keys()),
                mssing_name=name,
            )

        return lexical_scope[name]
