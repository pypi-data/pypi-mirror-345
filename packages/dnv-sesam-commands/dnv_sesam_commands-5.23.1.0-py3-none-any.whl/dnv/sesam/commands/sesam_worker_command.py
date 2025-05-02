"""This module contains the SesamWorkerCommand class."""

from typing import Optional

from .executable_command_base import ExecutableCommandBase


class SesamWorkerCommand(ExecutableCommandBase):
    """
    A base class for Sesam worker commands.
    """

    def __init__(
        self,
        working_dir: str = "",
    ):
        """
        Initializes a new instance of the SesamWorkerCommand class.

        Args:
            working_dir (str): The working directory for the command. Defaults to "".
        """
        super().__init__(working_dir)
        self.template_input_file = None
        self.input_file_name = None
        self.fem_file_name = None
        self.parameters = None
        self.arguments = None
        self.executable_folder = ""
        self.should_move_output_files = False
        self.output_files_to_exclude = []

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.SesamWorkerCommand, DNV.Sesam.Commons.SesamCommands"

    @property
    def input_file_name(self) -> Optional[str]:
        """
        Gets or sets the name of the input file.
        """
        return self.InputFileName

    @input_file_name.setter
    def input_file_name(self, value: Optional[str]):
        self.InputFileName = value

    @property
    def fem_file_name(self) -> Optional[str]:
        """
        Gets or sets the name of the FEM file.
        """
        return self.FemFileName

    @fem_file_name.setter
    def fem_file_name(self, value: Optional[str]):
        self.FemFileName = value

    @property
    def arguments(self) -> Optional[str]:
        """
        Gets or sets the additional arguments for the command.
        """
        return self.Arguments

    @arguments.setter
    def arguments(self, value: Optional[str]):
        self.Arguments = value

    @property
    def template_input_file(self) -> Optional[str]:
        """
        Gets or sets the template input file.
        """
        return self.TemplateInputFile

    @template_input_file.setter
    def template_input_file(self, value: Optional[str]):
        self.TemplateInputFile = value

    @property
    def parameters(self) -> Optional[dict[str, str]]:
        """
        Gets or sets the additional parameters for the command.
        """
        return self.Parameters

    @parameters.setter
    def parameters(self, value: Optional[dict[str, str]]):
        self.Parameters = value

    @property
    def executable_folder(self) -> str:
        """
        Gets or sets the folder containing the executable.
        """
        return self.ExecutableFolder

    @executable_folder.setter
    def executable_folder(self, value: str):
        self.ExecutableFolder = value
