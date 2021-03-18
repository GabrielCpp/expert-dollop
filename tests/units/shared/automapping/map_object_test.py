from unittest.mock import MagicMock
from dataclasses import dataclass
from expert_dollup.shared.automapping import Mapper


@dataclass
class Foo:
    name: str
    age: int


@dataclass
class Bar:
    name: str
    age: int


def map_foo_to_bar(src: Foo, mapper: Mapper = None) -> Bar:
    return Bar(name=src.name, age=src.age)


def test_given_identical_object_should_copy_each_member():
    expected_bar = Bar(name="Joe", age=18)
    foo = Foo(name="Joe", age=18)

    mapper = Mapper(MagicMock())
    mapper.add_mapping(Foo, Bar, map_foo_to_bar)

    bar = mapper.map(foo, Bar)

    assert bar == expected_bar
