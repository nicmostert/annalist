"""Annalist must never call the logged class's own __repr__, __str__ or __bool__.

Background
----------
Before a decorated ``__init__`` runs, the instance has no attributes yet. The
wrapper put the instance into a debug message with an f-string, which is
formatted immediately whether or not debug logging is on. That called the
class's own ``__repr__``, so a class like

    @ClassLogger
    def __init__(self, a): self.a = a
    def __repr__(self): return f"Thing({self.a})"

failed with ``AttributeError: 'Thing' object has no attribute 'a'`` the moment
it was constructed. The same applied to ``__bool__`` (the wrapper tested the
instance's truthiness) and to the property messages.

The rule: describe an instance with ``object.__repr__``, which cannot fail,
and never ask the instance whether it is true.
"""

from annalist.annalist import Annalist
from annalist.decorators import ClassLogger


def configure() -> None:
    """Configure Annalist with default settings."""
    Annalist().configure(analyst_name="test_repr_safety")


class ReprNeedsInit:
    """A class whose ``__repr__`` needs attributes that ``__init__`` sets."""

    @ClassLogger  # type: ignore
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        """Describe the instance, using an attribute set in ``__init__``."""
        return f"ReprNeedsInit({self.a})"

    @property
    def b(self):
        """Return ``b``."""
        return self._b

    @ClassLogger  # type: ignore
    @b.setter
    def b(self, value):
        """Set ``b``."""
        self._b = value

    @ClassLogger
    def method(self):
        """Return the attribute that ``__init__`` set."""
        return self.a


class StrAlwaysRaises:
    """A class whose ``__repr__`` and ``__str__`` always raise."""

    @ClassLogger  # type: ignore
    def __init__(self):
        self.ready = True

    def __repr__(self):
        """Raise, to prove that Annalist never calls it."""
        raise RuntimeError("repr must not be called")

    __str__ = __repr__

    @ClassLogger
    def method(self):
        """Return a value, uselessly."""
        return "ok"


class FalsyAndBroken:
    """A class whose ``__bool__`` always raises."""

    @ClassLogger  # type: ignore
    def __init__(self):
        self.ready = True

    def __bool__(self):
        """Raise, to prove that Annalist never calls it."""
        raise RuntimeError("bool must not be called")

    @ClassLogger
    def method(self):
        """Return a value, uselessly."""
        return "ok"


class TestReprThatNeedsInit:
    """Repr that needs init."""

    def test_construction_works(self):
        """Construction works."""
        configure()

        thing = ReprNeedsInit(5)

        assert repr(thing) == "ReprNeedsInit(5)"

    def test_methods_and_setters_work(self):
        """Methods and setters work."""
        configure()
        thing = ReprNeedsInit(5)

        thing.b = 7

        assert thing.method() == 5
        assert thing.b == 7


class TestReprThatAlwaysRaises:
    """Repr that always raises."""

    def test_logging_never_calls_it(self):
        """Logging never calls it."""
        configure()

        thing = StrAlwaysRaises()

        assert thing.method() == "ok"


class TestBoolThatAlwaysRaises:
    """Bool that always raises."""

    def test_logging_never_asks_whether_the_instance_is_true(self):
        """Logging never asks whether the instance is true."""
        configure()

        thing = FalsyAndBroken()

        assert thing.method() == "ok"
