from typing import NewType
from unittest.mock import MagicMock
from dataclasses import dataclass
from expert_dollup.shared.automapping import Mapper


def test_given_object_should_map_it_accordingly():
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

    expected_bar = Bar(name="Joe", age=18)
    foo = Foo(name="Joe", age=18)

    mapper = Mapper(MagicMock())
    mapper.add_mapping(Foo, Bar, map_foo_to_bar)

    bar = mapper.map(foo, Bar)

    assert bar == expected_bar


def test_given_newtype_dict_should_be_mapped_as_other_type_when_source_type_scpecified():
    Foo = NewType("Foo", dict)
    Bar = NewType("Bar", dict)

    def map_foo_to_bar(src: Foo, mapper: Mapper = None) -> Bar:
        return Bar({"age": src["age"], "name": src["name"]})

    expected_bar = dict(name="Joe", age=18)
    foo = dict(name="Joe", age=18)

    mapper = Mapper(MagicMock())
    mapper.add_mapping(Foo, Bar, map_foo_to_bar)

    bar = mapper.map(foo, Bar, Foo)

    assert bar == expected_bar
