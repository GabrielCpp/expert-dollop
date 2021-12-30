import ast


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
    def get_names(expression: str):
        formula_ast = ast.parse(expression)
        visitor = FormulaVisitor()
        visitor.visit(formula_ast)
        return visitor

    def __init__(self):
        self.var_names = set()
        self.fn_names = set()

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
