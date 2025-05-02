"""
This module defines the `ExecutableCommand` class, which represents a worker command for executing
an external executable file
"""

from dnv.onecompute.file_specification import FileSpecification
from dnv.oneworkflow.worker_command import WorkerCommand


class ExecutableCommand(WorkerCommand):
    """This class represents a worker command for executing an external executable file."""

    def __init__(
        self, filename: str, directory: str = "", args: str = "", working_dir: str = ""
    ):
        """
        Initializes a new instance of the ExecutableCommand class.

        Args:
            filename (str): The name of the executable file to run.
            directory (str, optional): The directory containing the executable file.
                Defaults to "", which means the directory points to the load case folder.
            args (str, optional): The command line arguments to pass to the executable.
                Defaults to "".
            working_dir (str, optional): The working directory for the command.
                Defaults to "", which means the working directory points to the load case folder.
        """
        super().__init__(working_dir)
        self.executable_file_specification = FileSpecification(
            filename=filename, directory=directory, sharedfolder=False
        )
        self.arguments = args

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.One.Workflow.CommandModel.ExecutableCommands.ExecutableCommand, DNV.One.Workflow.CommandModel"

    @property
    def executable_file_specification(self) -> FileSpecification:
        """
        Gets or sets the file specification of the executable file.
        """
        return self.ExecutableFileSpecification

    @executable_file_specification.setter
    def executable_file_specification(self, value: FileSpecification):
        self.ExecutableFileSpecification = value

    @property
    def arguments(self) -> str:
        """
        Gets or sets a string containing the command-line arguments for the executable.
        """
        return self.Arguments

    @arguments.setter
    def arguments(self, value: str):
        self.Arguments = value
