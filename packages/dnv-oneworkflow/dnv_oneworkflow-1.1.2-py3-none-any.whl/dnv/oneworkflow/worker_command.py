"""
The module contains the WorkerCommand class, which is a base class for defining worker commands.
It provides functionality for managing command attributes and working directories.
"""

import uuid

from dnv.onecompute.flowmodel import TypeMeta


class WorkerCommand(TypeMeta):
    """
    Base class for worker commands.

    The WorkerCommand class is used to define worker commands for various tasks.
    It manages command attributes and provides access to working directories.
    """

    def __init__(self, working_dir: str = ""):
        """
        Initializes a worker command.

        Args:
            working_dir (str, optional): The working directory for the command.
                Defaults to an empty string.
        """
        super().__init__()
        self.CommandId = str(uuid.uuid4())
        self.WorkingDirectory = working_dir

    @property
    def working_directory(self) -> str:
        """
        Gets or sets the working directory for the command.
        """
        return self.WorkingDirectory

    @working_directory.setter
    def working_directory(self, value: str):
        self.WorkingDirectory = value
