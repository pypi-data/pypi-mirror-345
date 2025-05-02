""" This module contains an enumeration representing different package repositories. """

from enum import Enum, unique


@unique
class Repository(str, Enum):
    """
    An enumeration representing different package repositories. This enum is used to
    differentiate between various package repositories based on their deployment stages:
    development, testing, and production.
    """

    DEV = "devpeuwst01owapps"
    """
    Identifier for the development repository. This repository typically contains packages that are
    currently under development and are used for developer testing.
    """

    TEST = "tstpeuwst01owapps"
    """
    Identifier for the test repository. This repository typically contains packages that have passed
    the development stage and are used for further testing by testers.
    """

    PROD = "prdpeuwst01owapps"
    """
    Identifier for the production repository. This repository typically contains packages that have
    passed all stages of testing and are ready for use by customers and end users.
    """
