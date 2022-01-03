from decimal import Decimal
from expert_dollup.core.units import ExpressionEvaluator


def test_expression_evaluator_simple_mul():
    evaluator = ExpressionEvaluator()
    result = evaluator.evaluate(
        "sum(value * factor for value in values) * cost",
        {
            "values": [Decimal(682)],
            "cost": Decimal("197.99"),
            "factor": Decimal("0.0005"),
            "sum": sum,
        },
    )
    assert result == Decimal("67.514590")
