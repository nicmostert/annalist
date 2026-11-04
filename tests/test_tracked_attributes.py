"""Tracked attributes when there is no instance.

Background
----------
A field named in a formatter, such as ``%(prop)s``, is filled in by looking
for an argument or an attribute of that name. For a method called through an
instance the attribute is read from the instance.

A classmethod or staticmethod called on the CLASS has no instance. Reading
the attribute from the class instead is useful for plain class variables, but
for a property it returns the property object itself:

    increment_value | prop: <property object at 0x7f...> | attr: 5

A property found on a class is not a value, so it must not be logged as one.
The same goes for any descriptor: methods, classmethods and staticmethods
found on the class are not values either.

The rules these tests pin down:

* Through an instance, attributes (properties included) are read from the
  instance, exactly as before.
* With no instance, plain class variables are logged and descriptors are not;
  the field is left as ``None``.
* ``__get__`` called by hand with no owner, as some tools do, still binds
  sensibly, and ``__get__(None, None)`` is rejected the way Python's own
  descriptors reject it.
"""

import pytest

from annalist.annalist import Annalist
from annalist.decorators import ClassLogger

FORMAT = "%(function_name)s :: %(value)s :: %(kind)s"


class Tracked:
    """A class with a plain class variable and a property, both tracked."""

    kind = "plain"  # a class variable: fine to log without an instance

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        """Return the stored value."""
        return self._value

    @ClassLogger
    @classmethod
    def build(cls, initial):
        """Build one.

        The argument is deliberately not called ``value``: a tracked field is
        filled from an argument of the same name before anything else, which
        would hide what these tests look at.
        """
        return cls(initial)

    @ClassLogger
    @staticmethod
    def helper():
        """Do nothing, usefully."""
        return 1

    @ClassLogger
    def instance_method(self):
        """Do nothing, through an instance."""
        return 2


def configure(name: str) -> None:
    """Configure Annalist to show the tracked fields."""
    Annalist().configure(analyst_name=name, stream_format_str=FORMAT)


def fields(capsys, function_name: str) -> list[str]:
    """Return ``[function_name, value, kind]`` from the one matching line."""
    (line,) = (
        line
        for line in capsys.readouterr().err.split("\n")
        if line.startswith(f"{function_name} ::")
    )
    return line.split(" :: ")


class TestWithNoInstance:
    """With no instance."""

    def test_a_property_is_not_logged_as_a_property_object(self, capsys):
        """A property is not logged as a property object."""
        configure("test_property_not_a_value")

        Tracked.helper()

        record = fields(capsys, "helper")
        assert "<property object" not in " ".join(record)
        assert record[1] == "None"

    def test_a_plain_class_variable_is_still_logged(self, capsys):
        """A plain class variable is still logged."""
        configure("test_class_variable_logged")

        Tracked.helper()

        assert fields(capsys, "helper")[2] == "plain"

    def test_the_same_holds_for_a_classmethod(self, capsys):
        """The same holds for a classmethod."""
        configure("test_classmethod_no_instance")

        Tracked.build(5)

        record = fields(capsys, "build")
        assert record[1] == "None"
        assert record[2] == "plain"

    def test_a_method_found_on_the_class_is_not_logged_as_a_value(self, capsys):
        # ``instance_method`` is a function on the class: a descriptor, not
        # a value. Track it by name to prove it is skipped.
        """A method found on the class is not logged as a value."""
        Annalist().configure(
            analyst_name="test_method_not_a_value",
            stream_format_str="%(function_name)s :: %(instance_method)s",
        )

        Tracked.helper()

        (line,) = (
            line
            for line in capsys.readouterr().err.split("\n")
            if line.startswith("helper ::")
        )
        assert line == "helper :: None"


class TestThroughAnInstance:
    """Through an instance."""

    def test_the_property_value_is_logged(self, capsys):
        """The property value is logged."""
        configure("test_property_value_via_instance")
        tracked = Tracked(42)
        capsys.readouterr()

        tracked.helper()

        assert fields(capsys, "helper")[1] == "42"

    def test_a_classmethod_through_an_instance_logs_the_property_value(self, capsys):
        """A classmethod through an instance logs the property value."""
        configure("test_classmethod_via_instance_property")
        tracked = Tracked(7)
        capsys.readouterr()

        tracked.build(1)

        assert fields(capsys, "build")[1] == "7"

    def test_an_ordinary_method_logs_the_property_value(self, capsys):
        """An ordinary method logs the property value."""
        configure("test_method_property_value")
        tracked = Tracked(9)
        capsys.readouterr()

        tracked.instance_method()

        assert fields(capsys, "instance_method")[1] == "9"


class TestDescriptorProtocolCalledDirectly:
    """Python always passes an owner to ``__get__``.

    The protocol allows ``descriptor.__get__(instance)`` without one, though,
    and some tools do exactly that.
    """

    def test_an_ordinary_method_without_an_owner_binds_the_instance(self):
        """An ordinary method without an owner binds the instance."""
        configure("test_get_without_owner")
        tracked = Tracked(1)

        bound = Tracked.__dict__["instance_method"].__get__(tracked)

        assert bound.__self__ is tracked

    def test_a_classmethod_without_an_owner_binds_the_instances_class(self):
        """A classmethod without an owner binds the instances class."""
        configure("test_classmethod_get_without_owner")

        class Sub(Tracked):
            pass

        bound = Tracked.__dict__["build"].__get__(Sub(1))

        assert bound.__self__ is Sub

    def test_no_instance_and_no_owner_is_rejected(self):
        # Python's own descriptors refuse this too.
        """No instance and no owner is rejected."""
        with pytest.raises(TypeError, match="__get__"):
            Tracked.__dict__["instance_method"].__get__(None, None)
