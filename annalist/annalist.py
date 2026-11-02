"""Main module."""

import inspect
import logging
import re
from os import PathLike

LOGGER_LEVELS = {
    "DEBUG": logging.DEBUG,
    10: logging.DEBUG,
    "INFO": logging.INFO,
    20: logging.INFO,
    "WARNING": logging.WARNING,
    30: logging.WARNING,
    "ERROR": logging.ERROR,
    40: logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    50: logging.CRITICAL,
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class AnnalistLogger(logging.Logger):
    """Custom Logger class to add contextual information."""

    def __init__(self, name, extra_attributes):
        """Construct a AnnalistLogger.

        Extends the functionality of the Logger class to accept user-defined
        fields as attributes.
        """
        if extra_attributes:
            self.extra_attributes = extra_attributes
        else:
            self.extra_attributes = []
        logging.Logger.__init__(self, name)
        logging.Logger.setLevel(self, logging.INFO)
        self.propagate = True

    def add_attributes(self, extra_attributes: list):
        """Add user-defined fields as attributes."""
        self.extra_attributes += extra_attributes

    def makeRecord(self, *args, **kwargs):  # type: ignore
        """Override Logger.makeRecord to accept user-defined fields."""
        rv = super().makeRecord(*args, **kwargs)
        for attr in self.extra_attributes:
            rv.__dict__[attr] = rv.__dict__.get(attr, None)
        return rv


class Singleton(type):
    """Singleton Metaclass.

    Ensures that only one instance of the inheriting class is created.
    """

    def __init__(self, name, bases, mmbs):
        """Enforce singleton upon new object creation."""
        super().__init__(name, bases, mmbs)
        self._instance = super().__call__()

    def __call__(self, *args, **kw):
        """Retrieve singleton object."""
        return self._instance


class Annalist(metaclass=Singleton):
    """Annalist Class.

    Attributes
    ----------
    logger : AnnalistLogger
        A custom subclass of logging.Logger which allows additional
        user-defined variables to be parsed from the formatter and added
        dynamically.
    stream_handler : logging.StreamHandler
        Logging handler that sends output to streams such as `sys.stdout`,
        `sys.stderr`, etc. Will be passed the `stream_formatter` attribute.
        See documentation for logging.StreamHandler for more info.
    file_handler : logging.FileHandler
        Logging handler that sends output to the logfile defined by the
        `logfile` attribute. Will be passed the `file_formatter` attribute.
        See `logging.FileHandler documentation`_ for more info.
    stream_formatter : str
        Stream formatting string to be parsed by `logging.Formatter`.
        Used to set up `stream_handler`.
        See `logging.Formatter documentation`_ for more info.
    file_formatter : str
        File formatting string to be parsed by `logging.Formatter`.
        See `logging.Formatter documentation`_ for more info.
    """

    _configured = False

    def __init__(self):
        """Annalist Constructor.

        Construsts an "unconfigured" instance of Annalist. However, since
        annalist is a singleton, it will simply retrieve a configured annalist
        if one exists somewhere in the namespace.
        """
        self.logger = AnnalistLogger("TempLogger", None)
        self.stream_handler = logging.StreamHandler()  # Log to console

    def configure(
        self,
        logfile: str | PathLike[str] | None = None,
        analyst_name: str | None = None,
        file_format_str: str | None = None,
        stream_format_str: str | None = None,
        level_filter: str = "INFO",
        default_level: str = "INFO",
    ):
        """Configure the Annalist."""
        self._analyst_name = analyst_name

        extra_attributes = []

        if file_format_str:
            file_format_attrs = self.parse_formatter(file_format_str)
            extra_attributes += file_format_attrs

        if stream_format_str:
            stream_format_attrs = self.parse_formatter(stream_format_str)
            extra_attributes += stream_format_attrs

        self.date_format = "%Y-%m-%d %H:%M:%S"
        default_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(analyst_name)s",
            self.date_format,
        )
        # Set up formatters
        if file_format_str:
            self.file_formatter = logging.Formatter(file_format_str, self.date_format)
        else:
            self.file_formatter = default_formatter
        if stream_format_str:
            self.stream_formatter = logging.Formatter(
                stream_format_str, self.date_format
            )
        else:
            self.stream_formatter = default_formatter

        self.logfile = logfile

        # Set up handlers
        if self.logfile:
            self.file_handler = logging.FileHandler(self.logfile, mode="w")
        self.stream_handler = logging.StreamHandler()  # Log to console

        default_attributes = [
            "analyst_name",
            "function_name",
            "function_doc",
            "ret_annotation",
            "params",
            "ret_val",
            "ret_val_type",
        ]

        self.all_attributes = default_attributes + extra_attributes

        self._default_level = LOGGER_LEVELS[default_level]

        self.logger = AnnalistLogger("auditor", self.all_attributes)

        if self.logfile:
            self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)

        if self.logfile:
            self.file_handler.setFormatter(self.file_formatter)

        self.stream_handler.setFormatter(self.stream_formatter)
        # self.set_stream_formatter(self.stream_formatter)

        self._level_filter = LOGGER_LEVELS[level_filter]

        self.logger.setLevel(self._level_filter)

        # Adding some more fields to the logger this way
        self._configured = True

    @property
    def analyst_name(self):
        """The analyst_name property."""
        if not self._configured:
            raise ValueError(
                "Annalist not configured. Configure object after retrieval."
            )
        return self._analyst_name

    @analyst_name.setter
    def analyst_name(self, value):
        """Set the analyst_name property.

        Name of the analyst who is invoking the script.

        Parameters
        ----------
        value : str
            The first
        """
        if not self._configured:
            raise ValueError(
                "Annalist not configured. Configure object after retrieval."
            )
        self._analyst_name = value

    @property
    def level_filter(self):
        """The level_filter property."""
        return self._level_filter

    @level_filter.setter
    def level_filter(self, value):
        self._level_filter = value
        self.logger.setLevel(self._level_filter)

    @property
    def default_level(self):
        """The default_level property."""
        return self._default_level

    @default_level.setter
    def default_level(self, value):
        """Set the default_level property."""
        self._default_level = value

    @staticmethod
    def parse_formatter(format_string):
        """Parse a formatting string.

        Extracts field names from a formatting string.
        Only `printf-style` (%-style) strings are supported.

        Parameters
        ----------
        format_string : str
            A `printf-style` (%-style) string.

        Returns
        -------
        list
            A list of parameter names in the order that they appear in the
            format string.

        .. _printf-style:
            https://docs.python.org/3/library/stdtypes.html#old-string-formatting`
        """
        return re.findall(r"%\((.*?)\)", format_string)

    def set_file_formatter(self, formatter, logfile: str | PathLike[str] | None = None):
        """Change the file formatter of the logger."""
        if self.logfile is None:
            if logfile is None:
                raise ValueError("Cannot set up file formatter, no log file specified.")
            else:
                self.logfile = logfile
            self.file_handler = logging.FileHandler(self.logfile)
        else:
            self.logger.removeHandler(self.file_handler)
            self.file_handler = logging.FileHandler(self.logfile)

        file_format_attrs = self.parse_formatter(formatter)
        self.logger.add_attributes(file_format_attrs)
        self.file_formatter = logging.Formatter(formatter, self.date_format)
        self.file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(self.file_handler)

    def set_stream_formatter(self, formatter):
        """Change the stream formatter of the logger."""
        stream_format_attrs = self.parse_formatter(formatter)
        self.logger.add_attributes(stream_format_attrs)
        self.logger.removeHandler(self.stream_handler)
        self.stream_formatter = logging.Formatter(formatter, self.date_format)
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.stream_formatter)
        self.logger.addHandler(self.stream_handler)

    def log_call(
        self,
        message,
        level,
        func,
        ret_val,
        extra_data,
        args=(),
        kwargs=None,
        *,
        skip_first=False,
    ):
        """Log function call.

        Parameters
        ----------
        args, kwargs
            The arguments the logged function was called with. They are
            ordinary parameters, not ``*args``/``**kwargs``, so that a logged
            function with a keyword called ``message`` or ``level`` cannot
            collide with this method's own parameters.
        skip_first
            Set for methods. The first parameter of ``func`` (``self`` or
            ``cls``) is then left out of the ``params`` field, because the
            caller does not pass it in ``args``.
        """
        if not self._configured:
            raise ValueError(
                "Annalist not configured. Configure object after retrieval."
            )

        report = {}
        signature = inspect.signature(func)
        if skip_first:
            signature = signature.replace(
                parameters=list(signature.parameters.values())[1:]
            )

        report["function_name"] = func.__name__
        report["function_doc"] = clean_str(func.__doc__)
        if signature.return_annotation == inspect._empty:
            report["ret_annotation"] = None
        else:
            report["ret_annotation"] = signature.return_annotation

        report["params"] = clean_str(describe_params(signature, args, kwargs))

        report["analyst_name"] = clean_str(self.analyst_name)
        report["ret_val_type"] = type(ret_val)
        report["ret_val"] = clean_str(ret_val)

        if extra_data:
            for key, val in extra_data.items():
                report[key] = val

        if level:
            logger_level = LOGGER_LEVELS[level]
        else:
            logger_level = self.default_level

        self.logger.log(
            logger_level,
            clean_str(message),
            extra=report,
        )


def describe_params(signature, args=(), kwargs=None):
    """Describe the arguments a function was called with.

    Returns ``{name: {"default", "annotation", "kind", "value"}}`` for every
    argument that was actually supplied, in the order of the signature.
    ``kind`` is ``"positional"`` if the argument was passed by position and
    ``"keyword"`` if it was passed by name.

    The arguments are matched to the signature by binding them, which is the
    same thing Python does, so ``*args``, ``**kwargs``, keyword-only and
    positional-only parameters are all matched correctly. Logging must never
    break the call it is describing, so if the arguments cannot be bound the
    result is empty.
    """
    kwargs = kwargs or {}
    try:
        bound = signature.bind_partial(*args, **kwargs)
    except TypeError:
        return {}

    positional_capable = [
        p.name
        for p in signature.parameters.values()
        if p.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    passed_by_position = set(positional_capable[: len(args)])

    params = {}
    for name, value in bound.arguments.items():
        param = signature.parameters[name]
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            kind = "positional"
        elif param.kind is inspect.Parameter.VAR_KEYWORD:
            kind = "keyword"
        else:
            kind = "positional" if name in passed_by_position else "keyword"
        params[name] = {
            "default": None if param.default is inspect._empty else param.default,
            "annotation": (
                None if param.annotation is inspect._empty else param.annotation
            ),
            "kind": kind,
            "value": value,
        }
    return params


def clean_str(s):
    """Clean a string for nice clean logging."""
    process = {
        ord("\t"): None,
        ord("\f"): " ",
        ord("\r"): None,
        ord(","): ";",
        ord("\n"): None,
    }
    s = str(s).translate(process)
    return s
