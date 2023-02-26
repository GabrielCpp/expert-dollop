import ast
from typing import Set


class SafeguardDivision(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp):
        if isinstance(node.op, ast.Div):
            return ast.Call(
                func=ast.Name(id="safe_div", ctx=ast.Load()),
                args=[
                    self.generic_visit(node.left),
                    self.generic_visit(node.right),
                ],
                keywords=[],
            )

        return self.generic_visit(node)


class FormulaVisitor(ast.NodeVisitor):
    whithelisted_node = set(
        [
            "Module",
            "Expr",
            "BinOp",
            "Num",
            "Sub",
            "Add",
            "Mult",
            "Div",
            "Call",
            "Subscript",
            "Attribute",
            "Index",
        ]
    )

    whithelisted_fn_names = set(["sqrt", "sin", "cos", "tan", "abs"])

    @staticmethod
    def get_names(expression: str) -> "FormulaVisitor":
        formula_ast = ast.parse(expression)
        visitor = FormulaVisitor()
        visitor.visit(formula_ast)
        return visitor

    def __init__(self):
        self.var_names: Set[str] = set()
        self.fn_names: Set[str] = set()

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node: ast.Call):
        self.fn_names.add(node.func.id)
        for a in node.args:
            self.visit(a)

        for a in node.keywords:
            self.visit(a)

    def visit_Name(self, node: ast.Name):
        self.var_names.add(node.id)

    def visit_Load(self, node):
        pass
