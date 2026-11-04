=======
History
=======

0.1.0 (2023-09-13)
------------------

* First release on PyPI.

0.1.1 (2023-10-27)
------------------

* Basic logging functionality.
* Only supports logging to console.

0.2.0 (2023-11-2)
------------------

* Implemented Annalist as a Singleton.
* Usage now includes configuration step.

0.3.0 (2023-11-20)
------------------

* Now takes arbitrary input paramaters.
* Able to support Hilltop audit trail parity.
* User can control logging levels

0.3.3 (2023-11-24)
------------------

* I'm not sure what happened to 0.3.1 and 0.3.2
* Now REALLLY able to support Hilltop audit trail parity.
* Improved support for class method logging

0.3.4 (2023-11-28)
------------------

* Fixed a bug with argument handling

0.3.5 (2023-11-29)
------------------

* Added basic string sanitation and truncating of long values in default message fields.

0.3.6 (2023-11-29)
------------------

* Now also sanitizing newline characters.

0.4.0 (2024-02-13)
------------------

* Moved to pyproject.toml package.
* Fixed bug relating to method identity crisis (decorated functions thought they were their decorators).

0.4.1 (2024-02-13)
------------------

* Fixed pyproject.toml package
* Updated .readthedocs.yaml to reflect changes in pyproject.toml

0.4.2 (2024-04-02)
------------------

* Relaxed Python dependency from 3.11.6 to 3.11

0.4.3 (2024-04-02)
------------------

* Considered being Ruff B905 compliant, but it turns out we're zipping over some unequal lists. Shelving this for later.
* Switched logfile mode from "append" to "write", which overwrites the logfile every time.

0.4.4 (2025-01-14)
------------------

* Added support for Python 3.12 onwards

0.4.5 (2026-06-02)
------------------

* Various package upgrades for compatibility
* Added support for Python 3.12 onwards

0.5.0 (unreleased)
------------------

Fixed:

* Calling a decorated class method or static method on the class itself (``MyClass.method()``) raised ``TypeError: __get__(None, None) is invalid``. It only worked on an instance. An ordinary method called through the class, ``MyClass.method(instance)``, failed in the same way. All now work, and class methods bind to the class that was used, so a subclass gets subclass instances back.
* Decorated methods now keep their identity (issue #9). The class dictionary held the wrapper, which had the signature ``(*args, **kwargs)`` and the docstring of ``ClassLogger``. A bound method still showed ``self`` (and ``cls``) in its signature, ``inspect.ismethod`` and ``inspect.isfunction`` said no, and ``inspect.signature(MyClass)`` showed ``self`` in the constructor. Decorated methods are now real functions and bound methods with the name, docstring, module and signature of the method that was written. Static type checkers still see the decorator and not the method.
* The ``params`` field was wrong for every method logged with ``ClassLogger``. For ``grow_craig(2.0)`` it recorded ``self`` as ``(2.0,)`` and the next parameter as ``{}``. It also flagged positional arguments as ``keyword``, and ``self``/``cls`` were counted as arguments. ``params`` now lists the arguments that were supplied, matched to the signature, without ``self`` and ``cls``.
* ``@function_logger`` on a function with a keyword argument named ``message``, ``level``, ``func`` or ``ret_val`` raised ``TypeError`` after the function had run.
* Reaching a decorated property through the class (``MyClass.prop``) raised ``AttributeError``. It now returns the property, like any property.
* A class with a decorated ``__init__`` and a ``__repr__`` that uses attributes set in ``__init__`` raised ``AttributeError`` on construction, because the log message called ``__repr__`` before ``__init__`` had run. Annalist no longer calls the logged class's ``__repr__``, ``__str__`` or ``__bool__``. As a result, decorating ``__repr__`` no longer recurses forever.
* With a class method or static method called on the class, a tracked attribute that is a property was logged as ``<property object ...>``. Only plain class variables are logged when there is no instance.
* Class methods now have ``cls`` left out of the arguments used to match tracked attributes, as ``self`` already was.

Changed:

* ``Annalist.log_call`` takes the logged function's ``args`` and ``kwargs`` as explicit parameters, where it took them as ``*args, **kwargs``. Nothing that calls ``log_call`` directly will keep working unchanged.
* The internal ``Wrapper.__call_method__`` hook is now ``__call_method__(self, instance, owner, /, *args, **kwargs)``. This only affects subclasses of ``Wrapper`` outside this package.
* Decorating a property getter with ``ClassLogger`` is documented as having no effect (it works, but reads are not logged). It was documented as an infinite loop.

Documentation:

* The README is rewritten. It described functions that do not exist (``add_stream_formatter``, ``configure(logger_name=...)``, ``@Annalist.annalize``), contained examples that could not run, and showed output that had never been produced. Every example is now run by the test suite, which also checks that the output it shows is what the README says.
* The README documents logging to a file, the ``params`` field, class methods and static methods, and levels.
* The API reference now includes ``annalist.decorators``, which holds ``ClassLogger`` and ``function_logger``. Docstring markup errors in the API docs are fixed, and the docs build without warnings.
* Installation instructions no longer refer to ``setup.py``.

Maintenance:

* ``test_all_fields`` no longer depends on the path the package is installed at.
* Removed files left over from before the move to ``pyproject.toml``: ``old_setup.py``, ``old_setup.cfg`` and ``old_requirements_dev.txt``; the scratch files ``temp_file.py`` and ``tests/example_script.py``; and a 2023 log file, ``tests/logfile.txt``.
* The ``Makefile`` no longer refers to ``tox``, ``flake8`` or an ``all`` extra, none of which exist.
* Python 3.12, 3.13 and 3.14 are listed in the package classifiers. The tests pass on 3.11 to 3.14.
