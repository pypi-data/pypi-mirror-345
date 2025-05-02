"""
This module offers the CreateInputFileFromInlineTemplateCommand class, which serves as a
representation of a worker command designed specifically for generating input files from a
template stored inline.
"""

from typing import Optional

from dnv.oneworkflow.create_input_file_from_template_command import (
    CreateInputFileFromTemplateCommand,
)


class CreateInputFileFromInlineTemplateCommand(CreateInputFileFromTemplateCommand):
    """
    This class represents a worker command that generates an input file from a template stored
    inline in a property. It dynamically replaces tagged parameters within the template with
    corresponding values from a provided parameter dictionary.
    """

    def __init__(
        self,
        working_dir: Optional[str] = None,
        input_filename: Optional[str] = "",
        parameters: Optional[dict[str, str]] = None,
        template: str = "",
    ):
        """
        Initializes a CreateInputFileFromInlineTemplateCommand object.

        Args:
            working_dir (Optional[str]): The working directory for the command. Defaults to None.
            input_filename (str): The name of the input file to be generated. The path should be
                relative to the `WorkerCommand.WorkingDirectory`
            parameters (dict[str, str]): A dictionary of parameters used for replacing values in the
                template.
            template (str): The template stored inline for generating the input file.
        """
        work_dir = working_dir if working_dir else ""
        super().__init__(
            working_dir=work_dir, input_filename=input_filename, parameters=parameters
        )
        self.Template: str = template

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.One.Workflow.CommandModel.ExecutableCommands.CreateInputFileFromInlineTemplateCommand, DNV.One.Workflow.CommandModel"

    @property
    def template(self) -> str:
        """
        Gets or sets the template stored inline for generating the input file.
        """
        return self.Template

    @template.setter
    def template(self, value: str):
        self.Template = value
