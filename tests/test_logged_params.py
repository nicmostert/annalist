"""The ``params`` field must describe the arguments the function was given.

Background
----------
Three things were wrong with ``params``:

* For every ``@ClassLogger`` method the field was nonsense. The wrapper passed
  the arguments to ``log_call`` as keywords called ``args`` and ``kwargs``,
  which ``log_call`` swallowed, so ``grow_craig(2.0)`` was logged as
  ``self = (2.0,)`` and ``feet = {}``.
* ``self`` and ``cls`` were treated as if the caller had supplied them.
* ``kind`` was inverted: an argument passed by position was logged as
  ``keyword``.

And a fourth, in the same call: ``log_call`` took the logged function's own
arguments as ``*args, **kwargs``, so ``@function_logger`` on a function with a
keyword called ``message``, ``level`` or ``func`` crashed with ``TypeError:
got multiple values for argument`` -- after the function had already run.
"""

import inspect

import pytest

from annalist.annalist import Annalist, describe_params
from annalist.decorators import function_logger
from tests.example_class import Craig


def signature_of(func):
    return inspect.signature(func)


def one(params: dict, name: str) -> dict:
    return params[name]


class TestDescribeParams:
    def test_a_positional_argument(self):
        def f(a, b=2): ...

        params = describe_params(signature_of(f), (1,), {})

        assert params == {"a": {"default": None, "annotation": None,
                                "kind": "positional", "value": 1}}

    def test_a_keyword_argument(self):
        def f(a, b=2): ...

        params = describe_params(signature_of(f), (1,), {"b": 5})

        assert one(params, "b")["kind"] == "keyword"
        assert one(params, "b")["value"] == 5
        assert one(params, "b")["default"] == 2

    def test_a_positional_or_keyword_argument_is_judged_by_how_it_was_passed(self):
        def f(a): ...

        assert one(describe_params(signature_of(f), (1,), {}), "a")["kind"] == "positional"
        assert one(describe_params(signature_of(f), (), {"a": 1}), "a")["kind"] == "keyword"

    def test_arguments_that_were_not_supplied_are_not_listed(self):
        def f(a, b=2, c=3): ...

        params = describe_params(signature_of(f), (1,), {})

        assert list(params) == ["a"]

    def test_annotations_are_recorded(self):
        def f(a: float): ...

        params = describe_params(signature_of(f), (1.5,), {})

        assert one(params, "a")["annotation"] is float

    def test_the_order_follows_the_signature_not_the_call(self):
        def f(a, b, c): ...

        params = describe_params(signature_of(f), (), {"c": 3, "a": 1, "b": 2})

        assert list(params) == ["a", "b", "c"]

    def test_star_args_and_star_kwargs(self):
        def f(a, *rest, **options): ...

        params = describe_params(signature_of(f), (1, 2, 3), {"x": 9})

        assert one(params, "rest") == {"default": None, "annotation": None,
                                       "kind": "positional", "value": (2, 3)}
        assert one(params, "options")["kind"] == "keyword"
        assert one(params, "options")["value"] == {"x": 9}

    def test_keyword_only_arguments_are_keyword(self):
        def f(a, *, flag=False): ...

        params = describe_params(signature_of(f), (1,), {"flag": True})

        assert one(params, "flag")["kind"] == "keyword"

    def test_arguments_that_do_not_fit_give_an_empty_result_not_an_error(self):
        # Logging must never break the call it describes.
        def f(a): ...

        assert describe_params(signature_of(f), (1, 2, 3), {}) == {}

    def test_no_arguments(self):
        def f(): ...

        assert describe_params(signature_of(f), (), None) == {}


def logged_params(capsys, function_name: str) -> str:
    """Return the logged ``params`` text for the last call of a function."""
    lines = [
        line
        for line in capsys.readouterr().err.split("\n")
        if line.startswith(f"{function_name} :: ")
    ]
    assert lines, f"no log line for {function_name}"
    return lines[-1].split(" :: ", 1)[1]


def configure():
    """Point Annalist's stream at stderr, showing only function and params.

    Called inside each test, after capsys is active. Configured in a fixture
    the handler would be bound to a capture stream that pytest has closed by
    the time the test body runs.
    """
    Annalist().configure(
        analyst_name="test_logged_params",
        stream_format_str="%(function_name)s :: %(params)s",
    )


class TestLoggedParamsForMethods:
    def test_an_ordinary_method_logs_its_real_arguments(self, capsys):
        configure()
        craig = Craig(surname="B", height=5.5, shoesize=9, injured=True, bearded=False)
        capsys.readouterr()

        craig.grow_craig(2.0)

        text = logged_params(capsys, "grow_craig")
        assert "'feet'" in text and "'value': 2.0" in text
        assert "'self'" not in text

    def test_a_keyword_argument_is_logged_as_keyword(self, capsys):
        configure()
        craig = Craig(surname="B", height=5.5, shoesize=9, injured=True, bearded=False)
        capsys.readouterr()

        craig.grow_craig(feet=2.0)

        assert "'kind': 'keyword'; 'value': 2.0" in logged_params(capsys, "grow_craig")

    def test_a_classmethod_does_not_log_cls_and_shows_its_argument(
        self, capsys
    ):
        configure()
        Craig.army_of_craigs(["Fisher"])

        text = logged_params(capsys, "army_of_craigs")
        assert "'surnames'" in text and "Fisher" in text
        assert "'cls'" not in text

    def test_a_staticmethod_has_nothing_skipped(self, capsys):
        configure()
        Craig.what_is_a_craig()

        assert logged_params(capsys, "what_is_a_craig") == "{}"

    def test_the_constructor_logs_its_arguments_without_self(self, capsys):
        configure()
        Craig(surname="B", height=5.5, shoesize=9, injured=True, bearded=False)

        text = logged_params(capsys, "__init__")
        assert "'surname'" in text and "'height'" in text
        assert "'self'" not in text

    def test_a_property_setter_logs_the_value_set(self, capsys):
        configure()
        craig = Craig(surname="B", height=5.5, shoesize=9, injured=True, bearded=False)
        capsys.readouterr()

        craig.shoesize = 11

        text = logged_params(capsys, "shoesize")
        assert "'value'" in text and "'value': 11" in text
        assert "'self'" not in text


class TestFunctionLoggerKeywordCollisions:
    @pytest.mark.parametrize("name", ["message", "level", "func", "ret_val"])
    def test_a_keyword_named_like_a_log_call_parameter_works(
        self, capsys, name
    ):
        configure()
        @function_logger
        def work(**options):
            return options[name]

        assert work(**{name: "hello"}) == "hello"

    def test_the_collision_is_logged_correctly(self, capsys):
        configure()
        @function_logger
        def work(message="a", level=1):
            return f"{message}{level}"

        assert work(message="hi", level=2) == "hi2"

        text = logged_params(capsys, "work")
        assert "'message'" in text and "'value': 'hi'" in text
        assert "'level'" in text and "'value': 2" in text
