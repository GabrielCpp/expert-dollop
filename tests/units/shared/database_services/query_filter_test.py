from typing import Optional
from expert_dollup.shared.database_services import QueryFilter


class FakeQueryFilter(QueryFilter):
    a: Optional[int]


def test_query_filter_retain_orginal_kwarg_dict():
    assert FakeQueryFilter().args == {}
    assert FakeQueryFilter(a=None).args == {"a": None}
    assert FakeQueryFilter(a=4).args == {"a": 4}
