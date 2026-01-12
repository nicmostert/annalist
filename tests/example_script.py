"""Just testing some stuff here."""

# from annalist.annalist import FunctionLogger
# from annalist.annalist import Annalist
import inspect
import logging

from annalist.annalist import Annalist
from annalist.decorators import function_logger
from tests.example_class import Craig, return_greeting, which_craig_is_that

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
#
ann = Annalist()

if __name__ == "__main__":
    format_str = (
        "%(levelname)s | %(function_name)s | %(message)s | %(injured)s | %(height)s"
    )
    ann.configure(
        analyst_name="Nic baby",
        stream_format_str=format_str,
        default_level="INFO",
        level_filter="INFO",
    )
    cb = Craig("Beaven", 5.5, 9, True, True)

    return_greeting("Craig")

    function_logger(
        which_craig_is_that,
        message="No decorator, just a quick peek",
        extra_info={"injured": "YEAH (in a lil jon voice)."},
    )("Craig")

    function_logger(
        inspect.unwrap(return_greeting),
        message="Redecorating a decorated function",
        extra_info={"injured": "OKAAAY (in a lil jon voice)."},
    )("Speve")
    print(cb.height)

    print(cb.surname)
    cb.surname = "Coulomb"
    print(cb.surname)
    cb.shoesize = 11
    print(cb.is_hurt_and_bearded())

    print("===================================================A")
    print(cb.height)
    print("===================================================B")
    cb.grow_craig(1.5)
    print("===================================================B")
    print(cb.height)
    print("===================================================A")
    army_surnames = [
        "Hawthorne",
        "Sandusky",
        "Gilgamesh",
        "Harriet",
        "Pilkington",
        "Reid",
        "Kannemeyer",
    ]

    army = cb.army_of_craigs(army_surnames)
    print(army)
