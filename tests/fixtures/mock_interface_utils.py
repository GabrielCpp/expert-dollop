from inspect import iscoroutinefunction, isfunction, getmembers, isabstract
from dataclasses import dataclass
from unittest.mock import MagicMock, PropertyMock, call
from collections import defaultdict
from deepdiff import DeepDiff
from typing import List, Tuple, Any, Dict


def return_async(value=None):
    async def async_property(*args, **kargs):
        return value

    return async_property


def raise_async(exception):
    async def _throw(*args, **kargs):
        raise exception

    return _throw


def raise_sync(exception):
    def _throw(*args, **kargs):
        raise exception

    return _throw


def get_methods(class_type):
    if isabstract(class_type):
        return class_type.__abstractmethods__

    return [
        name
        for name, _ in getmembers(class_type, predicate=isfunction)
        if not name in ("__init__", "__new__")
    ]


def mock_class(class_type, side_effects: dict = {}):
    raise_no_stub_async = lambda method_name: raise_async(
        Exception(f"Method {method_name} have not have a stub")
    )
    raise_no_stub = lambda method_name: raise_sync(
        Exception(f"Method {method_name} have not have a stub")
    )
    methods = {}
    repatchs = {}

    for method_name in get_methods(class_type):
        method = getattr(class_type, method_name)
        side_effect = (
            raise_no_stub_async(method_name)
            if iscoroutinefunction(method)
            else raise_no_stub(method_name)
        )

        if method_name in side_effects:
            side_effect = side_effects[method_name]

        if issubclass(type(method), property):
            methods[method_name] = PropertyMock()
            repatchs[method_name] = PropertyMock(side_effect=side_effect)
        else:
            methods[method_name] = MagicMock(side_effect=side_effect)

    if isabstract(class_type):
        instance = type(class_type.__name__, (class_type,), methods)()
    else:
        instance = type(class_type.__name__, (), methods)()

    for method_name, mock in repatchs.items():
        setattr(type(instance), method_name, mock)

    return instance


def compare_call_strict(lhs: call, rhs: call):
    all_args_are_same = all(a == b for a, b in zip(rhs[1], lhs[1]))

    all_kwargs_are_same = all(
        a_key == b_key and a_value == b_value
        for ((a_key, b_key), (a_value, b_value)) in zip(rhs[2].items(), lhs[2].items())
    )

    return all_args_are_same and all_kwargs_are_same


def compare_loose(
    lhs: Tuple[List[Any], Dict[str, Any]], rhs: Tuple[List[Any], Dict[str, Any]]
):
    lhs_call = call(*lhs[0], **lhs[1])
    rhs_call = call(*rhs[0], **rhs[1])

    arg_diff = DeepDiff(rhs_call[1], lhs_call[1])
    kwarg_diff = DeepDiff(rhs_call[2], lhs_call[2])
    return len(arg_diff) == 0 and len(kwarg_diff) == 0


def compare_per_arg(
    lhs: Tuple[List[Any], Dict[str, Any]], rhs: Tuple[List[Any], Dict[str, Any]]
):
    for lhs_arg, rhs_arg in zip(lhs[0], rhs[0]):

        if callable(rhs_arg):
            if rhs_arg(lhs_arg) == False:
                return False

            continue

        if not (lhs_arg == rhs_arg):
            return False

    if set(lhs[1].keys()) != set(rhs[1].keys()):
        return False

    for lhs_kwarg_key, rhs_kwarg_key in zip(lhs[1].keys(), rhs[1].keys()):
        rhs_kwarg = rhs[1][rhs_kwarg_key]
        lhs_kwarg = lhs[1][lhs_kwarg_key]

        if callable(rhs_kwarg) and rhs_kwarg(lhs_kwarg) == False:
            return False

        if not (lhs_kwarg == rhs_kwarg):
            return False

    return True


class Never:
    pass


class MatchingMockMismatch(Exception):
    def __init__(self, message, **props):
        Exception.__init__(self, message)
        self.props = props

    def __str__(self):
        prop_str = "  \n".join(f"{name}={value}" for name, value in self.props.items())
        return f"{Exception.__str__(self)} -> {prop_str}"


class StrictInterfaceSetup:
    class Proxy:
        def __init__(self):
            self.setup_method_name = None
            self.args = []
            self.kwargs = {}
            self.invoked = False

        def __getattr__(self, name):
            self.setup_method_name = name
            return self

        def __call__(self, *args, **kwargs):
            self.invoked = True
            self.args = args
            self.kwargs = kwargs

    @dataclass
    class CallCandidate:
        proxy: "StrictInterfaceSetup.Proxy"
        effect: callable
        is_equivalent: callable

        def __repr__(self):
            return str(self.invokation)

        @property
        def invokation(self) -> call:
            return call(*self.proxy.args, **self.proxy.kwargs)

    class Stub:
        def __init__(self, abstract_class):
            self.effect_by_calls: List[StrictInterfaceSetup.CallCandidate] = []
            self.method_name = None
            self.invoke_count = 0
            self.abstract_class = abstract_class.__name__

        def __call__(self, args, kwargs):
            invokation = call(*args, **kwargs)
            selected_effect = None
            for candidate in self.effect_by_calls:
                if len(invokation[1]) != len(candidate.invokation[1]):
                    continue

                if len(invokation[2]) != len(candidate.invokation[2]):
                    continue

                if len(invokation[1]) == 0 and len(invokation[2]) == 0:
                    selected_effect = candidate.effect
                    break

                if candidate.is_equivalent(
                    (args, kwargs), (candidate.proxy.args, candidate.proxy.kwargs)
                ):
                    selected_effect = candidate.effect
                    break

            if selected_effect is None:
                raise MatchingMockMismatch(
                    "No matching invokation found",
                    target=f"{self.abstract_class}.{self.method_name}",
                    invokation=str(invokation),
                    candidates=str(self.effect_by_calls),
                )

            self.invoke_count = self.invoke_count + 1

            return selected_effect(*args, **kwargs)

    def __init__(self, abstract_class):
        self._abstract_class = abstract_class
        self._setups_by_member_name = defaultdict(
            lambda: StrictInterfaceSetup.Stub(abstract_class)
        )
        self._properties = set()
        self.defers = self._build_defer_map(abstract_class)
        self.object = mock_class(abstract_class, self.defers)

    def setup(
        self,
        method,
        *args,
        compare_method=compare_loose,
        returns_async=Never,
        returns=Never,
        returnsSequence=None,
        invoke=None,
    ):
        effect = None
        proxy = StrictInterfaceSetup.Proxy()
        method(proxy)
        setup_method_name = proxy.setup_method_name
        methods = get_methods(self._abstract_class)

        if not setup_method_name is None and not setup_method_name in methods:
            raise Exception(
                "Method {} not found in {}".format(setup_method_name, methods)
            )

        if setup_method_name is None and not proxy.invoked:
            raise Exception("Proxy must be accessed to setup an attribute or method")

        if setup_method_name in self._properties and proxy.invoked:
            raise Exception("Property cannot be invoked")

        if not returns_async is Never:
            effect = return_async(returns_async)

        if not returns is Never:
            effect = lambda *args, **kwargs: returns

        if not returnsSequence is None:
            sequence = iter(returnsSequence)
            effect = lambda *args, **kwargs: next(sequence)

        if not invoke is None:
            effect = invoke

        if effect is None:
            raise Exception(
                "Should pass an effect between: returnsAsync, returns, returnsSequence, invoke"
            )

        stub = self._setups_by_member_name[setup_method_name]
        stub.method_name = setup_method_name
        stub.effect_by_calls.append(
            StrictInterfaceSetup.CallCandidate(proxy, effect, compare_method)
        )

    def assert_all_setup_called_in_order(self):
        assert (
            len(self._setups_by_member_name) > 0
        ), "Stub interface of {} must have at least one setup".format(
            self._abstract_class.__name__
        )

        for method_name, stub in self._setups_by_member_name.items():
            expected_mock_calls = [
                candidate.invokation for candidate in stub.effect_by_calls
            ]

            if method_name in self._properties:
                assert (
                    stub.invoke_count > 0
                ), "Stub for property {} must be called at least once".format(
                    method_name
                )
                continue

            method_mock = getattr(self.object, method_name)
            assert (
                method_mock.mock_calls == expected_mock_calls
            ), "For method {} expect {} but got {}".format(
                method_name, expected_mock_calls, method_mock.mock_calls
            )

    def assert_object_was_unused(self):
        for method_name in self._abstract_class.__abstractmethods__:
            if method_name in self._properties:
                continue

            method_mock = getattr(self.object, method_name)
            assert (
                len(method_mock.mock_calls) == 0
            ), "Expect methods {} of {} was never used".format(
                method_name, self._abstract_class.__name__
            )

    def _build_defer_map(self, abstract_class):
        def create_forwarder(method_name):
            def forward(*args, **kwargs):
                if not method_name in self._setups_by_member_name:
                    raise Exception(
                        f"No setup for method {abstract_class}.{method_name}"
                    )

                return self._setups_by_member_name[method_name](args, kwargs)

            return forward

        methods = {}

        for method_name in get_methods(abstract_class):
            methods[method_name] = create_forwarder(method_name)

            method = getattr(abstract_class, method_name)
            if issubclass(type(method), property):
                self._properties.add(method_name)

        return methods


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return MagicMock.__call__(self, *args, **kwargs)
