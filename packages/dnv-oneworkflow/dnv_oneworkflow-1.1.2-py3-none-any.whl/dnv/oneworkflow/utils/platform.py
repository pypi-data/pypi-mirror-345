"""This module defines the Platform enumeration, representing various computing platforms."""

from enum import Enum, unique


@unique
class Platform(Enum):
    """
    Enum class representing the different platforms that the application can run on.
    """

    WINDOWS = 0
    """
    An enum member indicating the Windows platform (with a value of 0).
    """

    LINUX = 1
    """
    An enum member indicating the Linux platform (with a value of 1).
    """
