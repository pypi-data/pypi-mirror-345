"""This module contains the GeniERuntimeCommand class."""

from .sesam_worker_command import SesamWorkerCommand


class GeniERuntimeCommand(SesamWorkerCommand):
    """
    A class for creating GeniERuntime commands to be executed by a worker.
    """

    def __init__(
        self,
        database_name: str = "model.gnx",
        input_file_name: str = "genie_in.js",
        options: str = "",
    ):
        """Initializes a new instance of the GeniERuntime class.

        Args:
            database_name (str): The name of the GeniE database to be created (gnx file).
            input_file_name (str): The name of the Javascript input file.
            options (str): Possible additional options to GeniERuntime.
        """
        super().__init__(working_dir="")
        self.input_file_name = input_file_name
        self.arguments = (
            f"--new {database_name} --com {input_file_name} {options} --exit"
        )

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.GeniE.GenieRuntimeCommand, DNV.Sesam.Commons.SesamCommands"
