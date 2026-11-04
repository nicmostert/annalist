"""A decorated method must look like the method that was written (issue #9).

Background
----------
Tools that inspect a class -- Sphinx autodoc, pydoc, linters, language
servers -- found the Annalist wrapper where the method should be:

* In the class dictionary the decorated method was a ``ClassLogger`` object
  with signature ``(*args, **kwargs)``, no ``__name__``, and the docstring of
  the ``ClassLogger`` class. So generated docs described Annalist, not the
  method.
* Looked up on an instance, ``craig.grow_craig`` was a ``functools.partial``:
  its signature still showed ``self``, ``inspect.ismethod`` said it was not a
  method, and ``craig.army_of_craigs`` still showed ``cls``.
* ``inspect.signature(Craig)`` showed ``self`` in the constructor.

The rule: after decoration, everything a tool can ask a method gives the same
answer as it would for the plain, undecorated method.

``Craig`` in ``tests/example_class.py`` is decorated with ``@ClassLogger`` on
an ordinary method, a classmethod, a staticmethod and ``__init__``.
"""

import inspect
import pydoc

import pytest

from annalist.annalist import Annalist
from tests.example_class import Craig

CONSTRUCTOR = "surname: str, height: float, shoesize: int, injured: bool, bearded: bool"


class SubCraig(Craig):
    """A subclass, to check what classmethods bind to."""


@pytest.fixture(autouse=True)
def _configured():
    Annalist().configure(analyst_name="test_identity")


@pytest.fixture()
def craig():
    """Return a Craig to test with."""
    return Craig(surname="Beaven", height=5.5, shoesize=9, injured=True, bearded=False)


def signature_of(obj) -> str:
    """Return the signature of an object as a string."""
    return str(inspect.signature(obj))


class TestTheClassDictionaryEntry:
    """What Sphinx, pydoc and getmembers_static find in ``Craig.__dict__``."""

    @pytest.mark.parametrize(
        ("name", "signature"),
        [
            ("grow_craig", "(self, feet: float)"),
            ("army_of_craigs", "(cls, surnames: list)"),
            ("what_is_a_craig", "()"),
            ("__init__", f"(self, {CONSTRUCTOR})"),
        ],
    )
    def test_the_signature_is_the_methods_not_args_kwargs(self, name, signature):
        """The signature is the methods not args kwargs."""
        assert signature_of(Craig.__dict__[name]) == signature

    @pytest.mark.parametrize(
        "name", ["grow_craig", "army_of_craigs", "what_is_a_craig", "__init__"]
    )
    def test_it_has_the_methods_name_and_location(self, name):
        """It has the methods name and location."""
        entry = Craig.__dict__[name]

        assert entry.__name__ == name
        assert entry.__qualname__ == f"Craig.{name}"
        assert entry.__module__ == "tests.example_class"

    @pytest.mark.parametrize(
        ("name", "first_line"),
        [
            ("grow_craig", "Grow your craig by specified amount of feet."),
            ("what_is_a_craig", "Explain a craig."),
            ("__init__", "Initialize a Craig."),
        ],
    )
    def test_the_docstring_is_the_methods_not_classloggers(self, name, first_line):
        """The docstring is the methods not classloggers."""
        doc = inspect.getdoc(Craig.__dict__[name])

        assert doc.splitlines()[0] == first_line
        assert "Decorate class methods" not in doc

    def test_it_points_back_at_the_original(self):
        """It points back at the original."""
        entry = Craig.__dict__["grow_craig"]

        assert inspect.unwrap(entry).__name__ == "grow_craig"


class TestLookedUpOnTheClass:
    """Looked up on the class."""

    def test_an_ordinary_method_is_a_plain_function(self):
        """An ordinary method is a plain function."""
        assert inspect.isfunction(Craig.grow_craig)
        assert type(Craig.grow_craig).__name__ == "function"
        assert signature_of(Craig.grow_craig) == "(self, feet: float)"

    def test_a_classmethod_is_a_method_bound_to_the_class(self):
        """A classmethod is a method bound to the class."""
        assert inspect.ismethod(Craig.army_of_craigs)
        assert Craig.army_of_craigs.__self__ is Craig
        assert signature_of(Craig.army_of_craigs) == "(surnames: list)"

    def test_a_classmethod_on_a_subclass_is_bound_to_the_subclass(self):
        """A classmethod on a subclass is bound to the subclass."""
        assert SubCraig.army_of_craigs.__self__ is SubCraig

    def test_a_staticmethod_is_a_plain_function(self):
        """A staticmethod is a plain function."""
        assert inspect.isfunction(Craig.what_is_a_craig)
        assert signature_of(Craig.what_is_a_craig) == "()"

    @pytest.mark.parametrize(
        "name", ["grow_craig", "army_of_craigs", "what_is_a_craig"]
    )
    def test_name_doc_and_module_survive(self, name):
        """Name doc and module survive."""
        method = getattr(Craig, name)

        assert method.__name__ == name
        assert method.__module__ == "tests.example_class"
        assert "Decorate class methods" not in (inspect.getdoc(method) or "")


class TestLookedUpOnAnInstance:
    """Looked up on an instance."""

    def test_an_ordinary_method_is_a_bound_method_without_self(self, craig):
        """An ordinary method is a bound method without self."""
        assert inspect.ismethod(craig.grow_craig)
        assert type(craig.grow_craig).__name__ == "method"
        assert craig.grow_craig.__self__ is craig
        assert signature_of(craig.grow_craig) == "(feet: float)"

    def test_a_classmethod_is_bound_to_the_class_not_the_instance(self, craig):
        """A classmethod is bound to the class not the instance."""
        assert inspect.ismethod(craig.army_of_craigs)
        assert craig.army_of_craigs.__self__ is Craig
        assert signature_of(craig.army_of_craigs) == "(surnames: list)"

    def test_a_classmethod_through_a_subclass_instance_binds_the_subclass(self):
        """A classmethod through a subclass instance binds the subclass."""
        sub = SubCraig(surname="B", height=5.5, shoesize=9, injured=True, bearded=False)

        assert sub.army_of_craigs.__self__ is SubCraig

    def test_a_staticmethod_is_a_plain_function(self, craig):
        """A staticmethod is a plain function."""
        assert inspect.isfunction(craig.what_is_a_craig)
        assert signature_of(craig.what_is_a_craig) == "()"

    def test_the_wrapped_function_is_reachable(self, craig):
        """The wrapped function is reachable."""
        assert inspect.unwrap(craig.grow_craig).__name__ == "grow_craig"


class TestTheClassItself:
    """The class itself."""

    def test_the_constructor_signature_has_no_self(self):
        # What a linter or language server shows when you type Craig(...).
        """The constructor signature has no self."""
        assert signature_of(Craig) == f"({CONSTRUCTOR})"

    def test_a_subclass_constructor_signature_has_no_self(self):
        """A subclass constructor signature has no self."""
        assert signature_of(SubCraig) == f"({CONSTRUCTOR})"


class TestDocumentationTools:
    """Documentation tools."""

    def test_pydoc_describes_the_methods_not_the_wrapper(self):
        """Pydoc describes the methods not the wrapper."""
        text = pydoc.render_doc(Craig, renderer=pydoc.plaintext)

        assert "Grow your craig by specified amount of feet." in text
        assert "Make an army of tall, healthy, shaven craigs." in text
        assert "Decorate class methods" not in text

    def test_getmembers_finds_the_methods_by_name(self):
        """Getmembers finds the methods by name."""
        names = {n for n, _ in inspect.getmembers(Craig, inspect.isroutine)}

        assert {"grow_craig", "army_of_craigs", "what_is_a_craig"} <= names


class TestBehaviourIsUnchanged:
    """Behaviour is unchanged."""

    def test_calls_still_work_and_return_values(self, craig):
        """Calls still work and return values."""
        assert craig.is_hurt_and_bearded() is False
        assert craig.measure_the_craig() == 5.5
        assert craig.measure_the_craig(7.0) == 7.0
        assert craig.what_is_a_craig() == "They sit next to me."
        assert [c.surname for c in craig.army_of_craigs(["A", "B"])] == ["A", "B"]

    def test_a_bound_method_can_be_stored_and_called_later(self, craig):
        """A bound method can be stored and called later."""
        grow = craig.grow_craig

        grow(1.0)

        assert craig.height == 6.5
