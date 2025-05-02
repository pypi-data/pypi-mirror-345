"""This module contains the SestraCommand class."""

from .sesam_worker_command import SesamWorkerCommand


class SestraCommand(SesamWorkerCommand):
    """
    A Sestra command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.Sestra.SestraCommand, DNV.Sesam.Commons.SesamCommands"
