"""
This module offers the PythonCommand class, which serves as a representation of a worker command 
designed specifically for the execution of Python script files.
"""

from typing import Optional

from dnv.onecompute.file_specification import FileSpecification
from dnv.oneworkflow.worker_command import WorkerCommand


class PythonCommand(WorkerCommand):
    """
    A class that represents a worker command for executing a Python script file.

    This class extends the WorkerCommand class and adds specific functionality for executing Python
    scripts. It allows for the execution of a Python script either from a file (specified by
    filename and directory) or from an inline script. If both are provided, the file script will be
    prioritized.

    Attributes:
        filename (str, optional): The name of the Python script file to run. Defaults to None.
        directory (str, optional): The directory containing the Python script file.
            Defaults to None.
        args (str, optional): The command line arguments to pass to the Python script.
            Defaults to None.
        working_dir (str, optional): The working directory for the Python script. Defaults to None.
        inline_script (str, optional): The inline Python script to be executed. Defaults to None.
    """

    def __init__(
        self,
        filename: Optional[str] = None,
        directory: Optional[str] = None,
        args: Optional[str] = None,
        working_dir: Optional[str] = None,
        inline_script: Optional[str] = None,
    ):
        """
        Initializes a PythonCommand object.

        This object represents a command to execute a Python script, which can be specified either
        as a file (Script File Specification) or as an inline script. If both are provided, the
        Script File Specification will take precedence.

        Args:
            filename (str, optional): The name of the executable file to run. Defaults to None
            directory (str, optional): The directory containing the executable file.
                Defaults to None, which means the directory points to the load case folder.
            args (str, optional): The command line arguments to pass to the executable.
                Defaults to an empty string.
            working_dir (str, optional): The working directory for the command.
                Defaults to "", which means the working directory points to the load case folder.
        """
        super().__init__(working_dir or "")
        self.script_file_specification = FileSpecification(
            filename=filename or "",
            directory=directory or "",
            sharedfolder=False,
        )
        self.arguments = args
        self.inline_script = inline_script

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.One.Workflow.CommandModel.ExecutableCommands.PythonCommand, DNV.One.Workflow.CommandModel"

    @property
    def script_file_specification(self) -> Optional[FileSpecification]:
        """
        Gets or sets the file specification of the Python script file.
        """
        return self.ScriptFileSpecification

    @script_file_specification.setter
    def script_file_specification(self, value: Optional[FileSpecification]):
        self.ScriptFileSpecification = value

    @property
    def inline_script(self) -> Optional[str]:
        """
        Gets or sets the inline Python script for the execution.
        """
        return self.InlineScript

    @inline_script.setter
    def inline_script(self, value: Optional[str]):
        self.InlineScript = value

    @property
    def arguments(self) -> Optional[str]:
        """
        Gets or sets the arguments for the command-line executable.
        """
        return self.Arguments

    @arguments.setter
    def arguments(self, value: Optional[str]):
        self.Arguments = value
