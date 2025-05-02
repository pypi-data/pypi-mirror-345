"""
This module offers the CreateInputFileFromFileTemplateCommand class, which serves as a
representation of a worker command designed for generating an input file from a template
stored in the file.
"""

from typing import Optional

from dnv.oneworkflow.create_input_file_from_template_command import (
    CreateInputFileFromTemplateCommand,
)


class CreateInputFileFromFileTemplateCommand(CreateInputFileFromTemplateCommand):
    """
    This class represents a worker command that generates an input file from a template stored
    in the file.
    """

    def __init__(
        self,
        working_dir: Optional[str] = None,
        input_filename: Optional[str] = "",
        parameters: Optional[dict[str, str]] = None,
        template_input_file: str = "",
    ):
        """
        Initializes a CreateInputFileFromFileTemplateCommand object.

        Args:
            working_dir (Optional[str]): The working directory for the command. Defaults to None.
            input_filename (str): The name of the input file to be generated. The path should be
                relative to the `WorkerCommand.WorkingDirectory`
            parameters (dict[str, str]): A dictionary of parameters used for replacing values in the
                template.
            template_input_file (str): The relative path to the template input file. The path should
                be relative to the 'WorkerCommand.WorkingDirectory'.
        """
        work_dir = working_dir if working_dir else ""
        super().__init__(
            working_dir=work_dir, input_filename=input_filename, parameters=parameters
        )
        self.TemplateInputFile: str = template_input_file

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.One.Workflow.CommandModel.ExecutableCommands.CreateInputFileFromFileTemplateCommand, DNV.One.Workflow.CommandModel"

    @property
    def template_input_file(self) -> str:
        """
        Gets or sets the relative path to a file containing template.

        The path should be relative to the 'WorkerCommand.WorkingDirectory'.
        """
        return self.TemplateInputFile

    @template_input_file.setter
    def template_input_file(self, value: str):
        self.TemplateInputFile = value
