from expert_dollup.shared.automapping import Aggregate


class ValueTypeAggregateProps:
    value_type: str
    config: NodeConfigValueType


class ValueTypeAggregate(Aggregate[ValueTypeAggregateProps]):
    def __init__(self):
        pass

    def _create(value_type: str, config: NodeConfigValueType) -> ValueTypeAggregate:
        pass