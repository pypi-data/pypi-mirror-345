"""This module contains the WadamCommand class."""

from .sesam_worker_command import SesamWorkerCommand


class WadamCommand(SesamWorkerCommand):
    """
    A Wadam command.

    This class represents a Wadam command, which is a specific type of Sesam worker command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.HydroCommands.Wadam.WadamCommand, DNV.Sesam.Commons.HydroCommands"
