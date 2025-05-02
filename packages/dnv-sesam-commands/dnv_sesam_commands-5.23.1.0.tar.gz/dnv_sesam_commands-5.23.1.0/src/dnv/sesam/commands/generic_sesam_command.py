"""This module contains the GenericSesamCommand class."""

from typing import Optional

from .sesam_worker_command import SesamWorkerCommand


class GenericSesamCommand(SesamWorkerCommand):
    """
    A generic Sesam command.
    """

    def __init__(self):
        """
        Initializes a new instance of the GenericSesamCommand class.
        """
        super().__init__(working_dir="")
        self.application = None
        self.default_executable_name = None
        self.executable_folder = ""

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.GenericSesamCommand, DNV.Sesam.Commons.SesamCommands"

    @property
    def application(self) -> Optional[str]:
        """
        Gets or sets the application for the command.
        """
        return self.Application

    @application.setter
    def application(self, value: Optional[str]):
        self.Application = value

    @property
    def default_executable_name(self) -> Optional[str]:
        """
        Gets or sets the default executable name.
        """
        return self.DefaultExecutableName

    @default_executable_name.setter
    def default_executable_name(self, value: Optional[str]):
        self.DefaultExecutableName = value
