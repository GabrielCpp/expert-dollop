from decimal import Decimal
from expert_dollup.core.units import ExpressionEvaluator

post_transform_factor_snippet = """
def get_post_transform_factor(unit_id, conversion_factor, special_condition):
    linear_unit_id = "linearunit" # 2
    brick_to_foot_id = "bricktofoot" # 11
    mul_conversion_factor = 1.0

    if (unit_id == linear_unit_id and special_condition) or unit_id != linear_unit_id:
        mul_conversion_factor = conversion_factor

    if mul_conversion_factor == 0:
        mul_conversion_factor = 1
    elif unit_id != brick_to_foot_id:
        mul_conversion_factor = 1/mul_conversion_factor
    
    return round_number(mul_conversion_factor, 8, 'truncate')


get_post_transform_factor(row['abstractproduct']['unit_id'], row['datasheet_element']['factor'], row['substage']['special_condition'])
"""


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
