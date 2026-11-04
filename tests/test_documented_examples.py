"""The examples in README.rst must do what the README says they do.

The README used to describe functions that do not exist (``add_stream_formatter``,
``configure(logger_name=...)``, ``@Annalist.annalize``), showed examples that
could not run, and printed output that had never been produced. These tests
run the examples as written and compare with the output shown.

Each test also checks that the output it expects appears in the README text,
so that if either the code or the README changes, one of them fails.

If you change an example in README.rst, change it here too.
"""

import inspect
import re
from pathlib import Path

import pytest

from annalist.annalist import Annalist
from annalist.decorators import ClassLogger, function_logger

README = (Path(__file__).parent.parent / "README.rst").read_text()


def stderr_lines(capsys) -> list[str]:
    """Return the non-empty lines written to stderr."""
    return [line for line in capsys.readouterr().err.split("\n") if line]


def shown_in_readme(text: str) -> None:
    """Fail unless the README shows this text."""
    assert text in README, f"README does not show: {text!r}"


class TestQuickStart:
    """Quick start."""

    def test_the_default_output_is_one_line_per_call(self, capsys):
        """The default output is one line per call."""
        ann = Annalist()
        ann.configure(analyst_name="Speve")

        @function_logger
        def example_function(): ...

        example_function()

        (line,) = stderr_lines(capsys)
        assert re.fullmatch(
            r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \| INFO \| auditor \| Speve", line
        )
        shown_in_readme("| INFO | auditor | Speve")

    def test_annalist_is_a_singleton(self):
        """Annalist is a singleton."""
        assert Annalist() is Annalist()


class TestFormatters:
    """Formatters."""

    def test_a_stream_format_given_to_configure(self, capsys):
        """A stream format given to configure."""
        ann = Annalist()
        ann.configure(
            analyst_name="Speve",
            stream_format_str="%(asctime)s, %(function_name)s",
        )

        @function_logger
        def example_function(): ...

        example_function()

        (line,) = stderr_lines(capsys)
        assert re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d, example_function", line)
        shown_in_readme("2023-11-02 09:42:13, example_function")

    def test_set_stream_formatter_changes_it_later(self, capsys):
        """Set stream formatter changes it later."""
        ann = Annalist()
        ann.configure(analyst_name="Speve")
        ann.set_stream_formatter("%(function_name)s | %(message)s")

        @function_logger(message="hello")
        def example_function(): ...

        example_function()

        assert stderr_lines(capsys) == ["example_function | hello"]

    def test_the_methods_the_readme_names_exist(self):
        """The methods the readme names exist."""
        ann = Annalist()
        for name in ("set_stream_formatter", "set_file_formatter"):
            assert hasattr(ann, name)
            shown_in_readme(name)
        assert not hasattr(ann, "add_stream_formatter")


class TestLoggingToAFile:
    """Logging to afile."""

    def test_a_logfile_gets_the_file_format(self, tmp_path, capsys):
        """A logfile gets the file format."""
        path = tmp_path / "audit.log"
        ann = Annalist()
        ann.configure(
            analyst_name="Speve",
            logfile=path,
            file_format_str=(
                "%(asctime)s, %(analyst_name)s, %(function_name)s | %(message)s"
            ),
        )

        @function_logger
        def example_function(): ...

        example_function()

        (line,) = path.read_text().strip().splitlines()
        assert re.fullmatch(
            r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d, Speve, example_function \|", line
        )
        shown_in_readme("2023-11-02 09:42:13, Speve, example_function |")

    def test_the_logfile_is_overwritten_each_time_annalist_is_configured(
        self, tmp_path, capsys
    ):
        """The logfile is overwritten each time annalist is configured."""
        path = tmp_path / "audit.log"
        ann = Annalist()

        @function_logger
        def example_function(): ...

        for _ in range(2):
            ann.configure(
                analyst_name="Speve",
                logfile=path,
                file_format_str="%(function_name)s",
            )
            example_function()

        assert path.read_text().strip().splitlines() == ["example_function"]
        shown_in_readme("overwritten every time Annalist is configured")

    def test_set_file_formatter_needs_a_logfile(self):
        """Set file formatter needs a logfile."""
        ann = Annalist()
        ann.configure(analyst_name="Speve")

        with pytest.raises(ValueError, match="no log file"):
            ann.set_file_formatter("%(function_name)s")


class TestAnnalizingClasses:
    """The ``ExampleClass`` from the README."""

    def make_class(self):
        """Build the ``ExampleClass`` from the README."""

        class ExampleClass:
            @ClassLogger  # type: ignore
            def __init__(self, arg1, arg2):
                self.arg1 = arg1
                self._arg2 = arg2

            @property
            def arg2(self):
                return self._arg2

            @ClassLogger  # type: ignore
            @arg2.setter
            def arg2(self, value):
                self._arg2 = value

            @ClassLogger  # type: ignore
            @classmethod
            def from_pair(cls, pair):
                """Build an instance from a pair of values."""
                return cls(*pair)

            @ClassLogger  # type: ignore
            @staticmethod
            def double(x):
                return x * 2

        return ExampleClass

    def configure(self):
        """Configure Annalist to show only the function name."""
        Annalist().configure(
            analyst_name="Speve", stream_format_str="%(function_name)s"
        )

    def test_every_decorated_method_is_logged(self, capsys):
        """Every decorated method is logged."""
        self.configure()
        ExampleClass = self.make_class()

        instance = ExampleClass(1, 2)
        instance.arg2 = 3
        ExampleClass.from_pair((4, 5))
        ExampleClass.double(2)

        assert stderr_lines(capsys) == [
            "__init__",
            "arg2",
            "__init__",
            "from_pair",
            "double",
        ]

    def test_class_and_static_methods_work_on_the_class_and_on_an_instance(self):
        """Class and static methods work on the class and on an instance."""
        self.configure()
        ExampleClass = self.make_class()
        instance = ExampleClass(1, 2)

        assert ExampleClass.double(4) == instance.double(4) == 8
        assert ExampleClass.from_pair((4, 5)).arg1 == 4
        assert instance.from_pair((4, 5)).arg1 == 4

    def test_a_decorated_property_getter_works_but_is_not_logged(self, capsys):
        # README: "An annalizer on the getter itself works, but has no effect."
        """A decorated property getter works but is not logged."""
        self.configure()

        class WithGetter:
            def __init__(self):
                self._x = 1

            @ClassLogger  # type: ignore
            @property
            def x(self):
                return self._x

        thing = WithGetter()

        assert thing.x == 1
        assert stderr_lines(capsys) == []
        shown_in_readme("reading a property is not logged")

    def test_annalizing_repr_is_safe(self, capsys):
        # The README used to warn that this recursed forever. It no longer
        # does, so the warning is gone.
        """Annalizing repr is safe."""
        self.configure()

        class Printable:
            def __init__(self):
                self.a = 1

            @ClassLogger
            def __repr__(self):
                return f"Printable({self.a})"

        assert repr(Printable()) == "Printable(1)"
        assert "DO NOT put an annalizer on the __repr__" not in README


class TestTheParamsField:
    """The params field."""

    def test_the_example_in_the_readme(self, capsys):
        """The example in the readme."""
        Annalist().configure(
            analyst_name="Speve", stream_format_str="%(function_name)s :: %(params)s"
        )

        class Craig:
            @ClassLogger  # type: ignore
            def grow_craig(self, feet: float):
                return feet

        Craig().grow_craig(2.0)

        (line,) = stderr_lines(capsys)
        expected = (
            "{'feet': {'default': None; 'annotation': <class 'float'>; "
            "'kind': 'positional'; 'value': 2.0}}"
        )
        assert line == f"grow_craig :: {expected}"
        shown_in_readme(expected)


class TestTrackingAttributes:
    """The ``MyClass`` walkthrough in the README, with its exact output."""

    def make_class(self):
        """Build the ``MyClass`` from the README."""

        class MyClass:
            @ClassLogger  # type: ignore
            def __init__(self, attr, prop):
                self.attr = attr
                self._prop = prop

            @property
            def prop(self):
                return self._prop

            @ClassLogger  # type: ignore
            @prop.setter
            def prop(self, value):
                self._prop = value

            @ClassLogger
            def square_attr(self):
                return self.attr**2

            @ClassLogger  # type: ignore
            @staticmethod
            def increment_value(attr):
                return attr + 1

        return MyClass

    def test_the_walkthrough(self, capsys):
        """The walkthrough."""
        ann = Annalist()
        ann.configure(analyst_name="Speve")
        ann.set_stream_formatter("%(function_name)s | prop: %(prop)s | attr: %(attr)s")
        MyClass = self.make_class()

        steps = [
            (lambda: MyClass(7, 2), "__init__ | prop: 2 | attr: 7"),
            (lambda mc: setattr(mc, "prop", 3), "prop | prop: 3 | attr: 7"),
            (lambda mc: mc.square_attr(), "square_attr | prop: 3 | attr: 7"),
            (lambda mc: mc.increment_value(5), "increment_value | prop: 3 | attr: 5"),
            (
                lambda mc: MyClass.increment_value(5),
                "increment_value | prop: None | attr: 5",
            ),
        ]
        mc = None
        for action, expected_line in steps:
            result = action() if mc is None else action(mc)
            if mc is None:
                mc = result
            assert stderr_lines(capsys) == [expected_line]
            shown_in_readme(expected_line)

    def test_the_returned_values(self):
        """The returned values."""
        Annalist().configure(analyst_name="Speve")
        MyClass = self.make_class()
        mc = MyClass(7, 3)

        assert mc.square_attr() == 49
        assert mc.increment_value(5) == 6
        assert MyClass.increment_value(5) == 6


class TestCustomFields:
    """Custom fields."""

    FORMAT = "%(function_name)s | %(site)s | %(hts_file)s | %(message)s"

    def test_extra_info_fills_the_custom_fields(self, capsys):
        """Extra info fills the custom fields."""
        Annalist().configure(analyst_name="Speve", stream_format_str=self.FORMAT)

        @function_logger(
            level="INFO",
            message="This decorator passes extra parameters",
            extra_info={"site": "Site one", "hts_file": "file.hts"},
        )
        def example_function(arg1, arg2): ...

        example_function(1, 2)

        assert stderr_lines(capsys) == [
            "example_function | Site one | file.hts "
            "| This decorator passes extra parameters"
        ]

    def test_fields_missing_from_the_decorator_default_to_none(self, capsys):
        """Fields missing from the decorator default to none."""
        Annalist().configure(analyst_name="Speve", stream_format_str=self.FORMAT)

        @function_logger
        def example_function(): ...

        example_function()

        assert stderr_lines(capsys) == ["example_function | None | None | "]

    def test_wrapper_mode(self, capsys):
        """Wrapper mode."""
        Annalist().configure(analyst_name="Speve", stream_format_str=self.FORMAT)

        def example_function(arg1, arg2):
            return arg1 + arg2

        result = function_logger(
            example_function,
            level="INFO",
            message="wrapped",
            extra_info={"site": "Site one", "hts_file": "file.hts"},
        )(1, 2)

        assert result == 3
        assert stderr_lines(capsys) == [
            "example_function | Site one | file.hts | wrapped"
        ]

    def test_the_formatter_names_and_extra_info_keys_in_the_readme_match(self):
        # The README example once formatted %(site)s but passed "site_name".
        """The formatter names and extra info keys in the readme match."""
        shown_in_readme('"site": "Site one"')
        shown_in_readme("%(site)s, %(hts_file)s")
        assert '"site_name"' not in README


class TestLevels:
    """Levels."""

    FORMAT = "%(levelname)s | %(function_name)s"

    def test_a_level_below_the_filter_is_not_written(self, capsys):
        """A level below the filter is not written."""
        Annalist().configure(
            analyst_name="Speve", stream_format_str=self.FORMAT, level_filter="WARNING"
        )

        @function_logger(level="DEBUG")
        def untracked_function(): ...

        untracked_function()

        assert stderr_lines(capsys) == []

    def test_lowering_the_filter_shows_it(self, capsys):
        """Lowering the filter shows it."""
        Annalist().configure(
            analyst_name="Speve", stream_format_str=self.FORMAT, level_filter="DEBUG"
        )

        @function_logger(level="DEBUG")
        def untracked_function(): ...

        untracked_function()

        assert stderr_lines(capsys) == ["DEBUG | untracked_function"]


class TestDecoratedMethodsKeepTheirIdentity:
    """Decorated methods keep their identity."""

    def test_the_readme_examples(self):
        """The readme examples."""
        Annalist().configure(analyst_name="Speve")

        class ExampleClass:
            @ClassLogger  # type: ignore
            def __init__(self, arg1, arg2):
                self.arg1 = arg1

            @ClassLogger  # type: ignore
            @classmethod
            def from_pair(cls, pair):
                """Build an instance from a pair of values."""
                return cls(*pair)

        assert str(inspect.signature(ExampleClass.from_pair)) == "(pair)"
        assert (
            ExampleClass.from_pair.__doc__ == "Build an instance from a pair of values."
        )
        assert str(inspect.signature(ExampleClass)) == "(arg1, arg2)"
        assert (
            str(inspect.signature(ExampleClass.__dict__["from_pair"])) == "(cls, pair)"
        )
        shown_in_readme("<Signature (pair)>")
        shown_in_readme("'Build an instance from a pair of values.'")
        shown_in_readme("<Signature (arg1, arg2)>")


def test_the_readme_does_not_mention_things_that_do_not_exist():
    """The readme does not mention things that do not exist."""
    for stale in ("add_stream_formatter", "logger_name", "Annalist.annalize"):
        assert stale not in README, f"README still mentions {stale}"
