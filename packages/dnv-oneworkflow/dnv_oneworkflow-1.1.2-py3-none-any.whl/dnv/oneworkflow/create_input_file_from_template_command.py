"""
This module offers the CreateInputFileFromTemplateCommand class, which serves as a representation of
a worker command designed specifically for generating input files from templates.
"""

from typing import Optional

from dnv.oneworkflow.worker_command import WorkerCommand


class CreateInputFileFromTemplateCommand(WorkerCommand):
    """
    This class represents a worker command that generates an input file from a template. It
    replaces tagged parameters within the template with corresponding values from a provided
    parameter dictionary.

    This base class includes information about the file name to be generated after the template
    processing from the dictionary of parameters and values. The derivatives of this class provide
    various methods for templatizing and creating input files, supporting the following approaches:
        - Inline template string
        - Using a file containing the template

    Please use the appropriate derived classes depending on the specific approach required.
    """

    def __init__(
        self,
        working_dir: Optional[str] = None,
        input_filename: Optional[str] = "",
        parameters: Optional[dict[str, str]] = None,
    ):
        """
        Initializes the CreateInputFileFromTemplateCommand class.

        Args:
            working_dir (Optional[str]): The working directory for the command. Defaults to None.
            input_filename (str): The name of the input file to be generated. The path should be
                relative to the `WorkerCommand.WorkingDirectory`
            parameters (dict[str, str]): A dictionary of parameters used for replacing values in the
                template.
        Returns:
            None
        """
        super().__init__(working_dir if working_dir else "")
        self.InputFileName = input_filename if input_filename else ""
        self.Parameters = parameters if parameters else dict[str, str]()

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.One.Workflow.CommandModel.ExecutableCommands.CreateInputFileFromTemplateCommand, DNV.One.Workflow.CommandModel"

    @property
    def input_filename(self) -> str:
        """
        Gets or sets the input file name, which may include a relative path, for generation.

        The relative path, if present, should be constructed with respect to
        'WorkerCommand.WorkingDirectory'.
        """
        return self.InputFileName

    @input_filename.setter
    def input_filename(self, value: str):
        self.InputFileName = value

    @property
    def parameters(self) -> dict[str, str]:
        """
        Gets or sets a dictionary of parameters used for replacing values in the template.
        """
        return self.Parameters

    @parameters.setter
    def parameters(self, value: dict[str, str]):
        self.Parameters = value
