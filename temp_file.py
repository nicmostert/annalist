"""Example of a class to be Annalized."""

# from annalist.annalist import Annalist, MethodDecorator
from annalist.annalist import Annalist
from annalist.decorators import ClassLogger, function_logger

ann = Annalist()

extra_info = {"injured": "Yessir."}


@function_logger(message="Just saying hi.", extra_info=extra_info)
def return_greeting(name: str = "loneliness") -> str:
    """Return a friendly greeting."""
    return f"Hi {name}"


def which_craig_is_that(sits: str = "left") -> str:
    """Which craig based on seat."""
    if sits == "left":
        return "Beaven"
    else:
        return "Coulomb"


class Craig:
    """A standard issue Craig."""

    # @ClassLogger  # type: ignore
    def __init__(
        self,
        surname: str,
        height: float,
        shoesize: int,
        injured: bool,
        bearded: bool,
    ):
        """Initialize a Craig."""
        self._surname = surname
        self._height = height
        self._shoesize = shoesize
        self.injured = injured
        self.bearded = bearded
        self.extra_info = {
            "injured": self.injured,
            "bearded": self.bearded,
        }

    @property
    def surname(self):  # type: ignore
        """The surname property."""
        return self._surname

    @ClassLogger
    @surname.setter
    def surname(self, value: str):
        """Set the surname of a Craig."""
        self._surname = value

    @property
    def shoesize(self):  # type: ignore
        """The shoesize property."""
        return self._shoesize

    @ClassLogger
    @shoesize.setter
    def shoesize(self, value: int):
        """Set the shoesize of your Craig."""
        self._shoesize = value

    @property
    def height(self):  # type: ignore
        """The height property."""
        return self._height

    @ClassLogger
    @height.setter
    def height(self, value):
        self._height = value

    @ClassLogger
    def grow_craig(self, feet: float):
        """Grow your craig by specified amount of feet."""
        self.height = self.height + feet  # type: ignore

    @ClassLogger
    def is_hurt_and_bearded(self) -> bool:
        """Return true if Craig is both injured and bearded."""
        return self.injured and self.bearded

    # This one has an input arg with the same name as a class attr.
    @ClassLogger
    def measure_the_craig(self, height: float | None = None) -> float:
        """Return true if Craig is both injured and bearded."""
        if height is None:
            return self.height
        else:
            return height

    @ClassLogger
    @staticmethod
    def what_is_a_craig():
        """Explain a craig."""
        return "They sit next to me."

    @ClassLogger
    @classmethod
    def army_of_craigs(cls, surnames: list):
        """Make an army of tall, healthy, shaven craigs."""
        army = []
        for surn in surnames:
            new_craig = cls(
                surname=surn,
                height=6.9,
                shoesize=11,
                injured=False,
                bearded=False,
            )
            army += [new_craig]

        return army

    # def __repr__(self) -> str:
    #     """Represent your Craig as a string."""
    #     return (
    #         f"Craig {self.surname} is {self.height} ft tall and wears "
    #         f"size {self.shoesize} shoes."
    #     )


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

    # print(return_greeting("Craig"))
    #
    # function_logger(
    #     which_craig_is_that,
    #     message="Post-logging an undecorated function here.",
    #     extra_info={"injured": "YEAH (in a lil jon voice)."},
    # )("Craig")
    #
    # print(function_logger(
    #     inspect.unwrap(return_greeting),
    #     message="Redecorating a decorated function",
    #     extra_info={"injured": "OKAAAY (in a lil jon voice)."},
    # )("Speve"))
    # print(cb.height)
    #
    print(cb.surname)
    #
    cb.surname = "Coulomb"
    # cb.shoesize = 11
    # print(cb.is_hurt_and_bearded())
    # print("=====================")
    # print(cb.is_hurt_and_bearded.__name__)
    # print(cb.is_hurt_and_bearded.__doc__)
    #
    # print("===================================================A")
    # print(cb.height)
    # print("===================================================B")
    # cb.grow_craig(1.5)
    # print("===================================================B")
    # print(cb.height)
    # print("===================================================A")
    # army_surnames = [
    #     "Hawthorne",
    #     "Sandusky",
    #     "Gilgamesh",
    #     "Harriet",
    #     "Pilkington",
    #     "Reid",
    #     "Kannemeyer",
    # ]
    #
    # army = cb.army_of_craigs(army_surnames)
    # print(army)
    #
    # print("===================================================C")
    # print(cb.army_of_craigs)
    # print(inspect.unwrap(cb.army_of_craigs))
