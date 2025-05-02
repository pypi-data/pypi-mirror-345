from enum import Enum, auto


class Sentinel(Enum):
    """
    Define a Sentinel type.

    See this for an explanation of the use-case for sentinels: https://peps.python.org/pep-0661/
    """

    MISSING = auto()
    NOT_GIVEN = auto()
