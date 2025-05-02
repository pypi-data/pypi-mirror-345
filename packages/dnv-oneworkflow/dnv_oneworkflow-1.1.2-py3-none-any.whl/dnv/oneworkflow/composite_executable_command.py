"""
This module defines the `CompositeExecutableCommand` class, which represents a composite of multiple
executable worker commands, allowing them to be executed sequentially or concurrently within a
specified working directory. It also provides properties to access and modify the execution mode and
the list of executable commands.
"""

from typing import Optional

from .worker_command import WorkerCommand


class CompositeExecutableCommand(WorkerCommand):
    """
    A command that represents a composite of multiple executable worker commands.

    This command allows a list of worker commands to be executed either sequentially
    or concurrently within a specific working directory.
    """

    def __init__(self, commands: list[WorkerCommand], working_dir: str = ""):
        """
        Initialize a CompositeExecutableCommand.

        Args:
            commands (list[WorkerCommand]): A list of worker commands to be executed.
            working_dir (str, optional): The working directory in which to execute the commands.
                Defaults to an empty string.
        """
        super().__init__(working_dir)

        # pylint: disable=invalid-name
        self.RunSequentially = True
        self.ExecutableCommands = commands
        self.ContinueOnError = False
        self.Input = None
        self.MaxDegreeOfParallelism = None
        for cmd in commands:
            if not cmd.working_directory.strip():
                cmd.working_directory = working_dir

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.One.Workflow.CommandModel.ExecutableCommands.CompositeExecutableCommand, DNV.One.Workflow.CommandModel"

    @property
    def run_sequentially(self) -> bool:
        """
        Gets or sets the execution mode for the commands.

        Execution mode determines if commands are run sequentially (True) or concurrently (False).
        The default mode is sequential.
        """
        return self.RunSequentially

    @run_sequentially.setter
    def run_sequentially(self, value: bool):
        self.RunSequentially = value

    @property
    def executable_commands(self) -> list[WorkerCommand]:
        """
        Gets or sets the list of worker commands to be executed.
        """
        return self.ExecutableCommands

    @executable_commands.setter
    def executable_commands(self, value: list[WorkerCommand]):
        self.ExecutableCommands = value

    @property
    def continue_onerror(self) -> bool:
        """
        Gets or sets a flag indicating whether to continue running the CompositeExecutable command
        if any WorkerCommand within it fails.

        When set to True, the CompositeExecutable command will keep running even if a command fails.
        In the case of failure, the overall execution status of the CompositeExecutable command will
        be marked as 'Faulted', regardless of individual command outcomes.
        """
        return self.ContinueOnError

    @continue_onerror.setter
    def continue_onerror(self, value: bool):
        self.ContinueOnError = value

    @property
    def max_degree_of_parallelism(self) -> Optional[int]:
        """
        Gets or sets the maximum degree of parallelism when running in parallel.
        """
        return self.MaxDegreeOfParallelism

    @max_degree_of_parallelism.setter
    def max_degree_of_parallelism(self, value: Optional[int]):
        self.MaxDegreeOfParallelism = value

    @property
    def input(self) -> Optional[object]:
        """
        Gets or sets the input to the task.
        """
        return self.Input

    @input.setter
    def input(self, value: Optional[object]):
        self.Input = value
