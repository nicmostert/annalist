"""Decorated classmethods and staticmethods must work when called on the class.

Background
----------
``@ClassLogger`` over ``@classmethod`` (or ``@staticmethod``) is documented as
supported, and it worked when called on an *instance*: ``craig.army_of_craigs()``.
Called on the *class*, which is the normal way to use a classmethod, it raised

    TypeError: __get__(None, None) is invalid

Python hands ``__get__`` the instance (``None`` for class access) AND the
owner class. The wrapper ignored the owner, then asked the classmethod to bind
to ``None``, which has no class to bind to.

The rules these tests pin down:

* Calling on the class works, returns the right value, and is logged.
* ``cls`` is the class that was actually used, so a subclass gets subclass
  instances back.
* The log message names the class, not ``NoneType``.
* Access through an instance, and ordinary methods, behave exactly as before.
* A classmethod argument called ``owner`` is an ordinary argument and is not
  swallowed by the wrapper.
"""

from annalist.annalist import Annalist
from annalist.decorators import ClassLogger
from tests.example_class import Craig

SEPARATOR = " :: "
FORMAT = SEPARATOR.join(
    ["%(analyst_name)s", "%(function_name)s", "%(levelname)s", "%(message)s"]
)


def configure(name: str) -> None:
    """Point Annalist's stream at stderr with a format the tests can split."""
    Annalist().configure(analyst_name=name, stream_format_str=FORMAT)


def log_records(capsys, function_name: str) -> list[list[str]]:
    """Return the logged lines for one function, split into their fields."""
    lines = capsys.readouterr().err.split("\n")
    records = [line.split(SEPARATOR) for line in lines if line]
    return [r for r in records if len(r) >= 4 and r[1] == function_name]


def make_craig() -> Craig:
    """Build a Craig with fixed values."""
    return Craig(surname="Beaven", height=5.5, shoesize=9, injured=True, bearded=False)


class SubCraig(Craig):
    """A subclass, to check that cls is the class that was used."""


class Registry:
    """Has a classmethod whose argument is literally called ``owner``."""

    def __init__(self, owner=None):
        self.owner = owner

    @ClassLogger
    @classmethod
    def build(cls, owner=None):
        """Build a Registry for an owner."""
        return cls(owner=owner)


class TestClassmethodOnTheClass:
    """Classmethod on the class."""

    def test_it_works_and_returns_the_right_thing(self):
        """It works and returns the right thing."""
        configure("test_classmethod_on_class_works")

        army = Craig.army_of_craigs(["Fisher", "Stewart-Baxter"])

        assert [c.surname for c in army] == ["Fisher", "Stewart-Baxter"]
        assert all(isinstance(c, Craig) for c in army)

    def test_it_is_logged(self, capsys):
        """It is logged."""
        configure("test_classmethod_on_class_logged")

        Craig.army_of_craigs(["Fisher"])

        assert len(log_records(capsys, "army_of_craigs")) == 1

    def test_the_log_message_names_the_class_not_nonetype(self, capsys):
        """The log message names the class not nonetype."""
        configure("test_classmethod_on_class_message")

        Craig.army_of_craigs(["Fisher"])

        (record,) = log_records(capsys, "army_of_craigs")
        message = record[3]
        assert "instance of Craig" in message
        assert "NoneType" not in message

    def test_a_subclass_gets_subclass_instances(self):
        """A subclass gets subclass instances."""
        configure("test_classmethod_on_subclass")

        army = SubCraig.army_of_craigs(["Fisher"])

        assert type(army[0]) is SubCraig

    def test_a_keyword_argument_called_owner_is_not_swallowed(self):
        """A keyword argument called owner is not swallowed."""
        configure("test_classmethod_owner_kwarg")

        registry = Registry.build(owner="somebody")

        assert registry.owner == "somebody"


class TestStaticmethodOnTheClass:
    """Staticmethod on the class."""

    def test_it_works_and_returns_the_right_thing(self):
        """It works and returns the right thing."""
        configure("test_staticmethod_on_class_works")

        assert Craig.what_is_a_craig() == "They sit next to me."

    def test_it_is_logged(self, capsys):
        """It is logged."""
        configure("test_staticmethod_on_class_logged")

        Craig.what_is_a_craig()

        assert len(log_records(capsys, "what_is_a_craig")) == 1

    def test_the_log_message_names_the_class_not_nonetype(self, capsys):
        """The log message names the class not nonetype."""
        configure("test_staticmethod_on_class_message")

        Craig.what_is_a_craig()

        (record,) = log_records(capsys, "what_is_a_craig")
        assert "NoneType" not in record[3]


class TestAccessThroughAnInstanceIsUnchanged:
    """Access through an instance is unchanged."""

    def test_classmethod_through_an_instance_still_works(self, capsys):
        """Classmethod through an instance still works."""
        configure("test_classmethod_via_instance")
        craig = make_craig()
        capsys.readouterr()  # discard the __init__ logging

        army = craig.army_of_craigs(["Fisher"])

        assert [c.surname for c in army] == ["Fisher"]
        assert len(log_records(capsys, "army_of_craigs")) == 1

    def test_classmethod_through_a_subclass_instance_binds_the_subclass(self):
        """Classmethod through a subclass instance binds the subclass."""
        configure("test_classmethod_via_subclass_instance")
        sub = SubCraig(
            surname="Beaven", height=5.5, shoesize=9, injured=True, bearded=False
        )

        army = sub.army_of_craigs(["Fisher"])

        assert type(army[0]) is SubCraig

    def test_staticmethod_through_an_instance_still_works(self, capsys):
        """Staticmethod through an instance still works."""
        configure("test_staticmethod_via_instance")
        craig = make_craig()
        capsys.readouterr()

        assert craig.what_is_a_craig() == "They sit next to me."
        assert len(log_records(capsys, "what_is_a_craig")) == 1

    def test_instance_and_class_access_are_logged_the_same_way(self, capsys):
        """Instance and class access are logged the same way."""
        configure("test_class_and_instance_log_alike")
        craig = make_craig()
        capsys.readouterr()

        craig.army_of_craigs(["Fisher"])
        via_instance = log_records(capsys, "army_of_craigs")
        Craig.army_of_craigs(["Fisher"])
        via_class = log_records(capsys, "army_of_craigs")

        # Same analyst, same function, same level, same message.
        assert via_instance[0][1:] == via_class[0][1:]


class TestOrdinaryMethodsAreUnchanged:
    """Ordinary methods are unchanged."""

    def test_an_instance_method_is_logged_with_its_instance(self, capsys):
        """An instance method is logged with its instance."""
        configure("test_instance_method_unchanged")
        craig = make_craig()
        capsys.readouterr()

        result = craig.measure_the_craig()

        assert result == 5.5
        (record,) = log_records(capsys, "measure_the_craig")
        assert "instance of Craig" in record[3]

    def test_a_method_called_through_the_class_still_runs(self):
        """A method called through the class still runs."""
        configure("test_unbound_method_call")
        craig = make_craig()

        # Craig.method(instance, ...) is legal Python and must keep working.
        assert Craig.measure_the_craig(craig, 7.0) == 7.0

    def test_a_method_called_through_the_class_is_logged_like_a_bound_call(
        self, capsys
    ):
        """A method called through the class is logged like a bound call."""
        configure("test_unbound_method_logging")
        craig = make_craig()
        capsys.readouterr()

        craig.measure_the_craig(7.0)
        bound = log_records(capsys, "measure_the_craig")
        Craig.measure_the_craig(craig, 7.0)
        unbound = log_records(capsys, "measure_the_craig")

        # The instance passed as the first argument is treated as the
        # instance, so the two calls produce the same log line.
        assert unbound == bound


class TestDecoratedPropertyReachedThroughTheClass:
    """``Craig.surname`` used to raise AttributeError: 'NoneType' ... '_surname'.

    The getter was being run with no instance. Like any property, reaching it
    through the class must give the property itself.
    """

    def test_it_returns_the_property_not_its_value(self):
        """It returns the property not its value."""
        assert isinstance(Craig.surname, property)

    def test_the_docstring_is_the_propertys(self):
        """The docstring is the propertys."""
        assert Craig.surname.__doc__ == "The surname property."

    def test_reading_and_setting_through_an_instance_still_work(self, capsys):
        """Reading and setting through an instance still work."""
        configure("test_property_via_instance")
        craig = make_craig()

        craig.surname = "Fisher"

        assert craig.surname == "Fisher"
