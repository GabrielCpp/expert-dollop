import ast
from expert_dollup.core.units.evaluator import FormulaVisitor


def test_visit_formula_should_find_formula_passed_as_fn_argument():
    ast_expr = ast.parse("mdcfg*(sqrt(sgchm*sgchm+sgpyg*sgpyg)*2)")
    formula_visitor = FormulaVisitor()
    formula_visitor.visit(ast_expr)
    assert formula_visitor.var_names == {"mdcfg", "sgchm", "sgpyg"}
