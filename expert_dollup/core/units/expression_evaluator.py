import ast
from decimal import Decimal
from expert_dollup.core.exceptions import AstEvaluationError


class ReturnSignal(Exception):
    def __init__(self, value):
        Exception.__init__(self, "Evaluate return")
        self.value = value


class AstVirtualMachine:
    def compute(self, node, scope):
        if isinstance(node, ast.FunctionDef):
            args_name = [a.arg for a in node.args.args]
            body = node.body

            def _compute_function(scope, args):
                fn_scope = dict(scope)
                fn_scope.update(dict(zip(args_name, args)))

                for element in body:
                    if isinstance(element, ast.Return):
                        value = self.compute(element.value, fn_scope)
                        return value

                    try:
                        self.compute(element, fn_scope)
                    except ReturnSignal as r:
                        return r.value

                return None

            scope[node.name] = _compute_function
            return _compute_function

        if isinstance(node, ast.Return):
            value = None if node.value is None else self.compute(node.value, scope)
            raise ReturnSignal(value)

        if isinstance(node, ast.GeneratorExp):
            elements = self.compute(node.generators[0].iter, scope)
            target = self.compute(node.generators[0].target, scope)
            values = []

            for element in elements:
                scope[target] = element
                value = self.compute(node.elt, scope)
                values.append(value)

            return values

        if isinstance(node, ast.If):
            result = self.compute(node.test, scope)

            if result:
                for element in node.body:
                    self.compute(element, scope)
            else:
                for element in node.orelse:
                    self.compute(element, scope)

            return None

        if isinstance(node, ast.Subscript):
            value = self.compute(node.value, scope)
            index = self.compute(node.slice.value, scope)

            return value[index]

        if isinstance(node, ast.Attribute):
            value = self.compute(node.value, scope)
            return getattr(value, node.attr)

        if isinstance(node, ast.Assign):
            targets = [self.compute(t, scope) for t in node.targets]
            value = self.compute(node.value, scope)

            for target in targets:
                scope[target] = value

            return scope[target]

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.Or):
                x = False

                for expr in node.values:
                    value = self.compute(expr, scope)
                    x = x or value

                return x

            elif isinstance(node.op, ast.And):
                x = True

                for expr in node.values:
                    value = self.compute(expr, scope)
                    x = x and value

                return x

            raise Exception("Unsupported BoolOp")

        if isinstance(node, ast.Expr):
            return self.compute(node.value, scope)

        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                assert node.id in scope, f"{node.id} not found"
                value = scope[node.id]
                return value

            return node.id

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, ast.Str):
            return node.s

        if isinstance(node, ast.UnaryOp):
            operand = self.compute(node.operand, scope)

            if isinstance(node.op, ast.UAdd):
                return +operand

            if isinstance(node.op, ast.USub):
                return -operand

            if isinstance(node.op, ast.Not):
                return not operand

            raise Exception("Unsupported unary op")

        if isinstance(node, ast.BinOp):
            left = self.compute(node.left, scope)
            right = self.compute(node.right, scope)

            if isinstance(node.op, ast.Add):
                return left + right

            if isinstance(node.op, ast.Sub):
                return left - right

            if isinstance(node.op, ast.Mult):
                assert isinstance(left, Decimal), type(left)
                assert isinstance(
                    right, Decimal
                ), f"Right id type of {type(right)} and value of {right}"
                return left * right

            if isinstance(node.op, ast.Div):
                try:
                    return left / right
                except ZeroDivisionError:
                    return 0

            raise Exception("Unsupported binary op")

        if isinstance(node, ast.Compare):
            left = self.compute(node.left, scope)
            result = left

            for comparator, op in zip(node.comparators, node.ops):
                right = self.compute(comparator, scope)

                if isinstance(op, ast.Eq):
                    result = left == right

                elif isinstance(op, ast.NotEq):
                    result = left != right

                elif isinstance(op, ast.Lt):
                    result = left < right

                elif isinstance(op, ast.LtE):
                    result = left <= right

                elif isinstance(op, ast.Gt):
                    result = left > right

                elif isinstance(op, ast.GtE):
                    result = left >= right

                else:
                    raise Exception("Unssuported comparator")

                left = right

            return result

        if isinstance(node, ast.Call):
            args = []

            for arg in node.args:
                result = self.compute(arg, scope)
                args.append(result)

            assert len(args) < 15

            if isinstance(node.func, ast.Name):
                if node.func.id in scope:
                    if scope[node.func.id].__name__ == "_compute_function":
                        return scope[node.func.id](scope, args)
                    else:
                        return scope[node.func.id](*args)

                raise Exception(f"Unknown function {node.func.id}")
            else:
                fn = self.compute(node.func, scope)
                result = fn(*args)
                return result

        raise Exception(f"Unsupported node {type(node)}")


class ExpressionEvaluator:
    def __init__(self):
        pass

    def evaluate(self, expression: str, scope: dict):
        formula_ast = ast.parse(expression)
        ast_vm = AstVirtualMachine()
        result = None
        for element in formula_ast.body:
            try:
                result = ast_vm.compute(element, scope)
            except Exception as e:
                raise AstEvaluationError(
                    "Error during evaluation of expression",
                    original_message=e,
                ) from e

        return result
