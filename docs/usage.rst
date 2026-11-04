=====
Usage
=====

Create an ``Annalist`` object, configure it, and decorate the functions and
methods that you would like to audit:

.. code-block:: python

    from annalist.annalist import Annalist
    from annalist.decorators import ClassLogger, function_logger

    ann = Annalist()
    ann.configure(
        analyst_name="Speve",
        stream_format_str="%(asctime)s | %(function_name)s | %(params)s",
    )

    @function_logger
    def add(a, b):
        return a + b

    class Counter:
        @ClassLogger  # type: ignore
        def __init__(self, start):
            self.value = start

        @ClassLogger
        def increment(self):
            self.value += 1

``function_logger`` decorates plain functions. ``ClassLogger`` decorates
methods, including ``__init__``, property setters, class methods and static
methods.

The sections of the :doc:`readme` go into more detail:

* `Formatters <readme.html#formatters>`_ and the fields that they can show.
* `Logging to a file <readme.html#logging-to-a-file>`_.
* `Tracking attributes <readme.html#tracking-attributes>`_ of a class.
* `Custom fields <readme.html#custom-fields>`_ and `levels <readme.html#levels>`_.

The :doc:`modules` page documents every function and class.
