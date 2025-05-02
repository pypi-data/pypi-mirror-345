"""This module contains the SesamCoreCommand class."""

from .executable_command_base import ExecutableCommandBase


class SesamCoreCommand(ExecutableCommandBase):
    """
    The base class for the Sesam core commands.
    """

    def __init__(
        self,
        working_dir: str = "",
        command: str = "fatigue",
        input_file_name: str = "SesamCore_input.json",
        options: str = "-hs",
    ):
        """
        Initializes a new instance of the SesamCoreCommand class.

        Args:
            working_dir (str, optional): The working directory for the command.
                Defaults to an empty string.
            command (str): The Sesam Core command to run. Defaults to "fatigue".
            input_file_name (str, optional): The name of the Sesam Core input file.
                Defaults to "SesamCore_input.json".
            options (str): The options to use with Sesam Core excluding the input file.
                Defaults to "-hs".
        """
        super().__init__(working_dir)
        self.command = command
        self.input_file_name = input_file_name
        self.options = options
        self.executable_folder = ""
        self.arguments = ""

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.SesamCore.SesamCoreCommand, DNV.Sesam.Commons.SesamCommands"

    @property
    def arguments(self) -> str:
        """
        Gets or sets the arguments for the command-line executable.
        """
        return self.Arguments

    @arguments.setter
    def arguments(self, value: str):
        self.Arguments = value

    @property
    def input_file_name(self) -> str:
        """
        Gets or sets the name of the Sesam Core input file.
        """
        return self.InputFileName

    @input_file_name.setter
    def input_file_name(self, value: str):
        self.InputFileName = value

    @property
    def command(self) -> str:
        """
        Gets or sets the Sesam Core command to run.
        """
        return self.Command

    @command.setter
    def command(self, value: str):
        self.Command = value

    @property
    def options(self) -> str:
        """
        Gets or sets the options to use with Sesam Core excluding the input file.
        """
        return self.Options

    @options.setter
    def options(self, value: str):
        self.Options = value

    @property
    def executable_folder(self) -> str:
        """
        Gets or sets the executable folder for Sesam Core.
        """
        return self.ExecutableFolder

    @executable_folder.setter
    def executable_folder(self, value: str):
        self.ExecutableFolder = value
