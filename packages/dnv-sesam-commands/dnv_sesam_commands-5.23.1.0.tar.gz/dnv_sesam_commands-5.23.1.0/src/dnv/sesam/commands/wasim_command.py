"""Module containing classes for different types of Wasim commands."""

from .sesam_worker_command import SesamWorkerCommand


class WasimSetupCommand(SesamWorkerCommand):
    """
    A Wasim setup command.

    This class represents a Wasim setup command, which is a specific type of Sesam worker command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.HydroCommands.Wasim.WasimSetupCommand, DNV.Sesam.Commons.HydroCommands"


class WasimStruCommand(SesamWorkerCommand):
    """
    A Wasim structural command.

    This class represents a Wasim structural command, which is a specific type of Sesam worker
    command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.HydroCommands.Wasim.WasimStruCommand, DNV.Sesam.Commons.HydroCommands"


class WasimFourierCommand(SesamWorkerCommand):
    """
    A Wasim Fourier command.

    This class represents a Wasim Fourier command, which is a specific type of Sesam worker
    command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.HydroCommands.Wasim.WasimFourierCommand, DNV.Sesam.Commons.HydroCommands"


class WasimSnapShotsCommand(SesamWorkerCommand):
    """
    A Wasim snapshots command.

    This class represents a Wasim snapshots command, which is a specific type of Sesam worker
    command.
    """

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.HydroCommands.Wasim.WasimSnapShotsCommand, DNV.Sesam.Commons.HydroCommands"


class WasimSolveCommand(SesamWorkerCommand):
    """
    A Wasim solve command.

    This class represents a Wasim solve command, which is a specific type of Sesam worker command.
    """

    def __init__(self, arguments: str = "/input=wasim_solve"):
        """
        Initializes a new instance of the SesamWorkerCommand class.

        Args:
            arguments (str): Additional arguments for the command.
        """
        super().__init__(working_dir="")
        self.arguments = arguments

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.HydroCommands.Wasim.WasimSolveCommand, DNV.Sesam.Commons.HydroCommands"
