import ast
from typing import List
from ..models import FlatAst
from .ast_serializer import AstSerializer, SIMPLE_AST_SERIALIZER, FULL_AST_SERIALIZER
from .visitors import SafeguardDivision


class ExpressionCompiler:
    @staticmethod
    def create_simple() -> "ExpressionCompiler":
        return ExpressionCompiler(
            AstSerializer(SIMPLE_AST_SERIALIZER), [SafeguardDivision()]
        )

    @staticmethod
    def create_complex() -> "ExpressionCompiler":
        return ExpressionCompiler(
            AstSerializer(FULL_AST_SERIALIZER), [SafeguardDivision()]
        )

    def __init__(
        self, serializer: AstSerializer, transformers: List[ast.NodeTransformer] = []
    ):
        self._serializer = serializer
        self._transformers = transformers

    def compile(self, expression: str) -> FlatAst:
        ast_transformed = ast.parse(expression)

        for transformer in self._transformers:
            transformer.visit(ast_transformed)

        return self._serializer.flatify(ast_transformed)

    def compile_to_dict(self, expression: str) -> dict:
        return self.compile(expression).dict()
