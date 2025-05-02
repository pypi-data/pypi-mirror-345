"""This module contains the WajacCommand class."""

from .sesam_worker_command import SesamWorkerCommand


class WajacCommand(SesamWorkerCommand):
    """
    A Wajac command.

    This class represents a Wajac command, which is a specific type of Sesam worker command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.Wajac.WajacCommand, DNV.Sesam.Commons.SesamCommands"
