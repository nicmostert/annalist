"""Logging Decorators."""

import functools
import inspect
import logging
from functools import partial

from annalist.annalist import Annalist

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

ann = Annalist()


def function_logger(
    _func=None,
    message: str = "",
    level: str | None = None,
    *,
    extra_info: dict | None = None,
):
    """Decorate a function to provide Annalist logging functionality.

    This function is used as either a decorator or a logger to provide
    Annalist logging functionality to a function.

    Examples
    --------
    ________
    When applied where the function is declared, this function serves as a
    decorator::

        @function_logger
        def example_function(arg1, arg2, ...):
            ...

    It can also be used where the function is called, and is then used as a
    wrapper::

        function_logger(example_function)(arg1, arg2, ...)

    In either case, ``function_logger`` can take optional arguments to specify
    a custom message, a log level, as well as any other info that needs to be
    sent to Annalist's formatter::

        @function_logger(
            message="Custom Message!",
            extra_info={
                "custom_field1": value1,
                "custom_field2": value2,
            },
        )
        def example_function(arg1, arg2, ...):
            ...

    or at calling time::

        function_logger(
            example_function,
            message="Custom Message!",
            extra_info={
                "custom_field1": value1,
                "custom_field2": value2,
            },
        )(arg1, arg2, ...)

    Parameters
    ----------
    _func : int, optional
        The function to be logged, either passed implicitly in the decorator
        case, or explicitly in the wrapper case. See examples.
    message : str, optional
        A custom message to be passed to the ``message`` field of the
        formatter. Note that this message will not appear if the message
        field is not present
        in the formatter.
    extra_info : dict, optional
        Extra info to be passed to the formatter. Keys in the dict should
        correspond to fields present in the formatter for them to show up.

    """

    def decorator_logger(func):
        # This line reminds func that it is func and not the decorator
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            ann.log_call(message, level, func, result, extra_info, *args, **kwargs)
            return result

        return wrapper

    # This section handles optional arguments passed to the logger
    if _func is None:
        return decorator_logger
    else:
        return decorator_logger(_func)


class Wrapper:
    """Wrapper that overrides some method hooks so that logging can happen."""

    def __init__(self, func, message=None):
        """Call the init function of super.

        Also puts the called function on the namespace.
        """
        _ = message
        super().__init__()
        self.func = func

    def __call__(self, *args, **kwargs):
        """Triggers when func is a function."""
        logger.debug("CALLING FUNCTION.")
        return self.func(*args, **kwargs)

    def __call_method__(self, instance, *args, **kwargs):
        """Call from LoggingDecorator.__call_method__."""
        logger.debug("+++++++++++++++++++++++++++++THIS IS THE SUPER CALL_METHOD")
        return self.func.__get__(instance)(*args, **kwargs)

    def __get_property__(self, instance, *args, **kwargs):
        """Made to be overridden."""
        return self.func.__get__(instance)(*args, **kwargs)

    def __set_property__(self, instance, *args, **kwargs):
        """Made to be overridden."""
        return self.func.__set__(instance)(*args, **kwargs)

    def __call_property__(self, instance, *args, **kwargs):
        """Made to be overridden."""
        return self.func.__call_property__(instance)(*args, **kwargs)

    def __get__(self, instance, args):
        """Triggers when instance.method() is called."""
        _ = args
        logger.debug(f"GETTER CALLED on {self.func}")
        logger.debug(f"is it a property? {isinstance(self.func, property)}")
        if isinstance(self.func, property):
            call_ret = self.__get_property__(instance)
            return call_ret
        else:
            call_ret = partial(self.__call_method__, instance)
            functools.update_wrapper(call_ret, self.func)
            return call_ret

    def __set__(self, instance, anything):
        """Triggers when setter is called."""
        logger.debug(f"SETTER CALLED on {self.func} with value {anything}")
        if isinstance(self.func, property):
            call_ret = self.__set_property__(instance, anything)
            return call_ret
        call_ret = partial(self.__call_property__, instance)
        functools.update_wrapper(call_ret, self.func)
        return call_ret


class ClassLogger(Wrapper):
    """Decorate class methods to provide Annalist functionality.

    Used as a decorator for class methods to provide Annalist logging.
    Unlike ``function_logger``, this decorator preserves knowledge of
    the class instance of the method that it decorates, which can be
    used to log information that is only available at runtime.

    This logger looks for input arguments instance that are named
    the same as custom fields in the formatter. If none such arguments
    are found, it looks for attributes on the parent class that match.
    If any are found, they are passed to Annalist to log them according
    to the formatter specification.

    Examples
    --------
    Class methods can be decorated with the ``ClassLogger`` to provide
    logging that preserves knowledge of the class instance. However,
    some linters have a difficult time understanding this syntax.
    For example, ``mypy`` does not like custom decorator on
    __init__, even though this is perfectly legal code. In this case,
    add the linter comment ``# type: ignore`` inline:

        class MyClass:
            @ClassLogger  # type: ignore
            def __init__(self, prop1, ...):
                self._prop1 = prop1
                ...

    It is also possible to decorate properties. These should be decorated
    on the ``setter``, and not the ``@property``. Once again,
    ``mypy`` is not a big fan of this syntax, so add the ``# type: ignore``
    line if necessary::

            @property
            def prop1(self):
                return self._prop1

            @ClassLogger  # type: ignore
            @prop1.setter
            def prop1(self, value):
                self._prop1 = value

    Do not decorate the ``@property`` method itself. This creates an infinite
    loop, as the logger calls the property, which calls the property ...

    Normal methods, static methods, and class methods can be decorated as
    normal.

            @ClassLogger
            def normal_method(self, arg):
                ...

            @ClassLogger
            @staticmethod
            def static_method(arg):
                ...

            @ClassLogger
            @classmethod
            def class_method(cls, arg):
                ...

    I haven't tried all the magic methods. ``__init__`` works fine.
    ``__repr__`` does not, it does the infinite loop thing.

    """

    def __call__(self, *args, **kwargs):
        """Triggers when a function is called.

        Logs, then sends to Wrapper.__call__.
        """
        logger.debug(f"FUNCTION CALLED {self.func}")
        logger.debug(
            f"You decorated a function called {self.func.__name__} "
            f"with args {args}, and kwargs {kwargs}"
        )
        ret_val = super().__call__(*args, **kwargs)
        ret_val_str = trunc_value_string(ret_val)
        logger.info(f"FUNCTION {self.func} called with args {args} and {kwargs}")
        logger.info(f"FUNCTION {self.func} RETURNS {ret_val_str}")
        return ret_val

    def __call_method__(self, instance, *args, **kwargs):
        """Triggers when a method is called (through __get__).

        Logs, then sends to Wrapper.__call_method__.
        """
        logger.debug("METHOD seen, let's get it.")
        logger.debug(
            f"You decorated a method called {self.func.__name__} "
            f"with instance {instance}, "
            f"args {args}, and kwargs {kwargs}"
        )
        ret_val = super().__call_method__(instance, *args, **kwargs)
        logger.info(f"METHOD {self.func} called with args {args} and {kwargs}")
        logger.info(f"METHOD {self.func} is on {instance}")
        logger.info(f"METHOD {self.func} RETURNS {ret_val}")
        ret_val_str = trunc_value_string(ret_val)
        message = (
            f"METHOD {self.func.__qualname__} called with "
            + f"args {args} and kwargs {kwargs}. "
            + f"It is on an instance of {instance.__class__.__name__}, "
            + f"and returns the value {ret_val_str}."
        )

        if hasattr(self.func, "__wrapped__"):
            ret_func = inspect.unwrap(self.func)
        else:
            ret_func = self.func

        # I'm unwrapping here in case the func is a
        # classmethod (which is a wrapper).
        fill_data = self._inspect_instance(ret_func, instance, args, kwargs)

        ann.log_call(
            message=message,
            level=ann.default_level,
            func=ret_func,
            ret_val=ret_val,
            extra_data=fill_data,
            args=args,
            kwargs=kwargs,
        )
        logger.debug("DONE LOGGING METHOD")
        return ret_val

    def __get_property__(self, instance, *args, **kwargs):
        """Triggers when a property is called (through __get__).

        Logs, then sends to Wrapper.__call_property__
        """
        _ = args
        _ = kwargs
        logger.debug("PROPERTY seen, let's get it.")
        logger.debug(
            f"You decorated a property called {self.func.fget} on instance {instance}, "
        )
        value = self.func.fget(instance)
        logger.debug(f"PROPERTY IS {value}")
        return value

    def __set_property__(self, instance, value):
        """Triggers when a property setter is called.

        Logs, then sends to Wrapper.__set_property__
        """
        logger.debug("PROPERTY seen, let's SET it.")
        logger.debug(
            f"You decorated a property called {self.func.fset} on instance {instance}, "
        )
        logger.debug("Inspecting Instance:")
        fill_data = self._inspect_instance(
            self.func.fset,
            instance,
            [],
            {},
            setter_value={self.func.fset.__name__: value},
        )

        val_str = trunc_value_string(value)

        message = (
            f"PROPERTY {self.func.fset.__qualname__} "
            + f"SET TO {val_str}. "
            + f"It is on an instance of {instance.__class__.__name__}."
        )
        ann.log_call(
            message=message,
            level=ann.default_level,
            func=self.func.fset,
            ret_val=None,
            extra_data=fill_data,
            args=value,
            kwargs=None,
        )

        logger.info(f"PROPERTY {self.func.fset} SET TO {value}")
        return self.func.fset(instance, value)

    @staticmethod
    def _inspect_instance(func, instance, args, kwargs, setter_value=None):
        if setter_value is None:
            setter_value = {}
        logger.debug(f"RAW ARGS: {args}")
        logger.debug(f"RAW KWARGS: {kwargs}")
        # arg_values = list(args) + list(kwargs.values())
        argspec = inspect.getfullargspec(func)
        logger.debug(f"argspec: {argspec}")

        if (len(argspec.args) > 0) and (argspec.args[0] == "self"):
            func_args = argspec.args[1:]
        else:
            func_args = argspec.args

        fill_data = {}

        arg_values = {}

        for key, val in zip(func_args[: len(args)], args):
            arg_values[key] = val

        arg_values.update(kwargs)

        if len(setter_value) != 0:
            arg_values.update(setter_value)
            if list(setter_value.keys())[0] in ann.all_attributes:
                fill_data = setter_value

        logger.debug(f"Fill data: {fill_data}")
        logger.debug(f"Function Arguments: {func_args}")
        logger.debug(f"Argument Values: {arg_values}")
        logger.debug(f"Setter Values: {setter_value}")
        logger.debug(f"Looking for: {ann.all_attributes}")
        # if is_setter:
        #     if func.__name__ in ann.all_attributes:

        for attr in ann.all_attributes:
            logger.debug(f"Searcing for {attr}")
            if attr in fill_data:
                pass
            elif attr in func_args:
                logger.info(f"Found {attr} in method args.")
                if attr in arg_values.keys():
                    fill_data[attr] = arg_values[attr]
                elif hasattr(instance, attr):
                    logger.info(
                        f"But no arg supplied.Found {attr} in class attributes."
                    )
                    fill_data[attr] = getattr(instance, attr)
                else:
                    logger.info("Arg not supplied, and not in class attributes")
            elif hasattr(instance, attr):
                logger.info(f"Found {attr} in class attributes.")
                fill_data[attr] = getattr(instance, attr)

        logger.debug(f"fill_data = {fill_data}")

        return fill_data


def trunc_value_string(value):
    """Construct a short truncated string repr of a long value."""
    val_str = str(value)
    if len(val_str) > 20:
        val_type = type(value)
        if hasattr(value, "__len__"):
            val_len = len(value)
            val_str = val_str[:20] + f" ... [{val_type} " + f"of len {val_len}]"
        else:
            val_str = val_str[:20] + f" ... [long {val_type} (trunc)]"
    return val_str
