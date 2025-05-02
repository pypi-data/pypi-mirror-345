"""This module contains the CalibrationCommand class."""

from typing import Optional

from .executable_command_base import ExecutableCommandBase


class CalibrationCommand(ExecutableCommandBase):
    """
    The base class for the Sesam core commands.
    """

    def __init__(
        self,
        input_parameters_file_name: Optional[str] = None,
        pisa_results_file_name: Optional[str] = None,
        calibration_directory: Optional[str] = None,
    ):
        super().__init__(working_dir="")
        self.input_parameters_file_name = input_parameters_file_name
        self.pisa_results_file_name = pisa_results_file_name
        self.calibration_directory = calibration_directory

    @property
    def type(self) -> str:
        """
        Gets the type of the command.
        """
        return "DNV.Sesam.Commons.SesamCommands.Infidep.CalibrationCommand, DNV.Sesam.Commons.SesamCommands"

    @property
    def input_parameters_file_name(self) -> Optional[str]:
        """
        Gets or sets the name of the calibration input file.
        """
        return self.InputParametersFileName

    @input_parameters_file_name.setter
    def input_parameters_file_name(self, value: Optional[str]):
        self.InputParametersFileName = value

    @property
    def pisa_results_file_name(self) -> Optional[str]:
        """
        Gets or sets the name of the calibration input file.
        """
        return self.PisaResultsFileName

    @pisa_results_file_name.setter
    def pisa_results_file_name(self, value: Optional[str]):
        self.PisaResultsFileName = value

    @property
    def calibration_directory(self) -> Optional[str]:
        """
        Gets or sets the path to the directory containing the calibration code.

        For cloud runs, this should be left as None.
        """
        return self.CalibrationDirectory

    @calibration_directory.setter
    def calibration_directory(self, value: Optional[str]):
        self.CalibrationDirectory = value
