"""This module contains the WorkerCommandExtended class."""

from typing import List, Optional

from dnv.oneworkflow.worker_command import WorkerCommand


class ExecutableCommandBase(WorkerCommand):
    """
    Represents an extended worker command with additional properties.

    The ExecutableCommandBase class is an extended version of the WorkerCommand class, offering
    enhanced control over command execution and output file management. While the base
    WorkerCommand class provides fundamental attributes such as a unique command id and a
    working directory, the ExecutableCommandBase class goes a step further.

    It introduces additional properties including command arguments, the executable_folder,
    and file handling options. These enhancements dictate which output files should be moved
    or retained post command execution, providing a granular level of control over the
    execution process and output file management.

    For instance, the `arguments` property allows for the specification of additional command
    line arguments. The `executable_folder` property designates the folder housing the executable
    command. The file handling options provide control over the destination of output files,
    determining whether they should be moved to the command's working directory or remain in
    their original locations.
    """

    def __init__(
        self,
        working_dir: str = "",
        arguments: str = "",
        executable_folder: str = "",
        should_move_output_files: bool = False,
        output_files_to_include: Optional[List[str]] = None,
        output_files_to_exclude: Optional[List[str]] = None,
    ):
        """
        Represents an extended worker command with additional properties.
        This class serves as an extension of the Worker Command pattern and inherits from the base
        WorkerCommand class.

        Args:
            working_dir (str, optional): The working directory for the command.
                Defaults to an empty string.
            arguments (str): The arguments to be passed to the command.
            executable_folder (str): The folder where the executable command is located.
            should_move_output_files (bool): A value indicating whether the command's output files,
                located in sub-folders, should be moved to the parent directory, the command's
                working directory.
            output_files_to_include (Optional[List[str]]): A list of glob patterns representing
                files that will be moved from their locations to the command's working directory.
                Defaults to ["**/**"], which includes all files in the command's working directory
                and subdirectories.
            output_files_to_exclude (Optional[str]): A list of glob patterns representing files that
                will remain in their locations during the file moving process.
                Defaults to an empty list, which includes no files.
        """
        super().__init__(working_dir)
        # The following attributes are named in PascalCase due to compatibility with an existing
        # codebase or API. Pylint warnings are disabled for these lines to allow this naming
        # convention.
        self.Arguments = arguments  # pylint: disable=invalid-name
        self.ExecutableFolder = executable_folder  # pylint: disable=invalid-name
        self.ShouldMoveOutputFiles = (  # pylint: disable=invalid-name
            should_move_output_files
        )
        self.OutputFilesToInclude = (  # pylint: disable=invalid-name
            output_files_to_include
            if output_files_to_include is not None
            else ["**/**"]
        )
        self.OutputFilesToExclude = (  # pylint: disable=invalid-name
            output_files_to_exclude if output_files_to_exclude is not None else []
        )

    @property
    def arguments(self) -> str:
        """
        Gets or sets the arguments to be passed to the command.
        """
        return self.Arguments

    @arguments.setter
    def arguments(self, value: str):
        self.Arguments = value

    @property
    def executable_folder(self) -> str:
        """
        Gets or sets the folder where the executable command is located.
        """
        return self.ExecutableFolder

    @executable_folder.setter
    def executable_folder(self, value: str):
        self.ExecutableFolder = value

    @property
    def should_move_output_files(self) -> bool:
        """
        Gets or sets a value indicating if output files in sub-folders of the command's working
        directory should be moved to the working directory itself.
        """
        return self.ShouldMoveOutputFiles

    @should_move_output_files.setter
    def should_move_output_files(self, value: bool):
        self.ShouldMoveOutputFiles = value

    @property
    def output_files_to_include(self) -> List[str]:
        """
        Gets or sets a list of glob patterns representing files that will be moved from their
        locations to command's working directory during the file relocation process.

        If None is passed, the list is set to ["**/**"], which includes all files in the command's
        working directory and its sub-directories.
        """
        return self.OutputFilesToInclude

    @output_files_to_include.setter
    def output_files_to_include(self, value: Optional[List[str]]):
        self.OutputFilesToInclude = value if value is not None else ["**/**"]

    @property
    def output_files_to_exclude(self) -> List[str]:
        """
        Gets or sets a list of glob patterns representing files that will remain in their original
        locations during the file relocation process.

        If None is passed, an empty list is assigned, which includes no files.
        """
        return self.OutputFilesToExclude

    @output_files_to_exclude.setter
    def output_files_to_exclude(self, value: Optional[List[str]]):
        self.OutputFilesToExclude = value if value is not None else []
