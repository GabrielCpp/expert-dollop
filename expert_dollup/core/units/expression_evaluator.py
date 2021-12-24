import ast


class AstVirtualMachine:
    def __init__(self, scope: dict):
        self.scope = scope

    def compute(self, node, scope=None):
        scope = scope or self.scope

        if isinstance(node, ast.FunctionDef):
            args_name = [a.arg for a in node.args.args]
            body = node.body

            def _compute_function(scope, args):
                fn_scope = dict(scope)
                fn_scope.update(dict(zip(args_name, args)))

                for element in body:
                    if isinstance(element, ast.Return):
                        value, _ = self.compute(element.value, fn_scope)
                        return value, ""

                    self.compute(element, fn_scope)

                return None, ""

            self.scope[node.name] = _compute_function
            return _compute_function, ""

        if isinstance(node, ast.GeneratorExp):

            def _compute_generator():
                elements, _ = self.compute(node.generators[0].iter, scope)
                target, _ = self.compute(node.generators[0].target, scope)

                for element in elements:
                    scope[target] = element
                    value, _ = self.compute(node.elt, scope)
                    yield value

            return _compute_generator()

        if isinstance(node, ast.If):
            result, _ = self.compute(node.test, scope)

            if result:
                for element in node.body:
                    self.compute(element, scope)
            elif node.orelse:
                for element in node.orelse:
                    self.compute(element, scope)

            return None, ""

        if isinstance(node, ast.Subscript):
            value, details = self.compute(node.value, scope)
            index, details2 = self.compute(node.slice.value, scope)

            return value[index], f"{details}[{details2}]"

        if isinstance(node, ast.Assign):
            targets = [self.compute(t, scope)[0] for t in node.targets]
            value, _ = self.compute(node.value, scope)

            for target in targets:
                scope[target] = value

            return scope[target], ""

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.Or):
                x = False

                for expr in node.values:
                    value, _ = self.compute(expr, scope)
                    x = x or value

                return x, ""

            elif isinstance(node.op, ast.And):
                x = True

                for expr in node.values:
                    value, _ = self.compute(expr, scope)
                    x = x and value

                return x, ""

            raise Exception("Unsupported BoolOp")

        if isinstance(node, ast.Attribute):
            print(node.value)
            print(node.attr)
            assert False

        if isinstance(node, ast.Expr):
            return self.compute(node.value, scope)

        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                assert node.id in scope, f"{node.id } not in {self.scope}"
                value = scope[node.id]
                return value, f"{value}"

            return node.id, f"{node.id}"

        if isinstance(node, ast.Constant):
            return node.value, f"{node.value}"

        if isinstance(node, ast.Num):
            return node.n, f"{node.n}"

        if isinstance(node, ast.Str):
            return node.s, f"{node.s}"

        if isinstance(node, ast.UnaryOp):
            operand = self.compute(node.operand, scope)

            if isinstance(node.op, ast.UAdd):
                return +operand, f"+{operand}"

            if isinstance(node.op, ast.USub):
                return -operand, f"-{operand}"

            if isinstance(node.op, ast.Not):
                return not operand, f"!{operand}"

            raise Exception("Unsupported unary op")

        if isinstance(node, ast.BinOp):
            left, left_details = self.compute(node.left, scope)
            right, right_details = self.compute(node.right, scope)

            if isinstance(node.op, ast.Add):
                return left + right, f"{left_details} + {right_details}"

            if isinstance(node.op, ast.Sub):
                return left - right, f"{left_details} - {right_details}"

            if isinstance(node.op, ast.Mult):
                return left * right, f"{left_details} * {right_details}"

            if isinstance(node.op, ast.Div):
                try:
                    return left / right, f"{left_details} * {right_details}"
                except ZeroDivisionError:
                    return 0, ""

            raise Exception("Unsupported binary op")

        if isinstance(node, ast.Compare):
            left, left_details = self.compute(node.left, scope)
            result = left
            details = f"{left_details}"

            for comparator, op in zip(node.comparators, node.ops):
                right, right_details = self.compute(comparator, scope)

                if isinstance(op, ast.Eq):
                    result = left == right
                    details = details + f" == {right_details}"

                elif isinstance(op, ast.NotEq):
                    result = left != right
                    details = details + f" != {right_details}"

                elif isinstance(op, ast.Lt):
                    result = left < right
                    details = details + f" < {right_details}"

                elif isinstance(op, ast.LtE):
                    result = left <= right
                    details = details + f" <= {right_details}"

                elif isinstance(op, ast.Gt):
                    result = left > right
                    details = details + f" > {right_details}"

                elif isinstance(op, ast.GtE):
                    result = left >= right
                    details = details + f" >= {right_details}"
                else:
                    raise Exception("Unssuported comparator")

                left = right

            return result, details

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise Exception("Functino only support direct reference")

            args = []
            details = []

            for arg in node.args:
                result, calculation_details = self.compute(arg, scope)
                args.append(result)
                details.append(calculation_details)

            assert len(args) < 15

            if node.func.id in scope:
                if scope[node.func.id].__name__ == "_compute_function":
                    return scope[node.func.id](scope, args), ""
                else:
                    return scope[node.func.id](*args), ""

            raise Exception(f"Unknown function {node.func.id}")

        raise Exception(f"Unsupported node {type(node)}")


class ExpressionEvaluator:
    def __init__(self):
        pass

    def evaluate(self, expression: str, scope: dict):
        formula_ast = ast.parse(expression)
        ast_vm = AstVirtualMachine(scope)
        result = None
        for element in formula_ast.body:
            result, _ = ast_vm.compute(element)

        return result
