from typing import Any, Optional

from dnv.oneworkflow.worker_command import WorkerCommand

from ._type_converter import TypeConverter

def execute_command(
    cmd: WorkerCommand, type_converter: Optional[TypeConverter] = None
) -> Any:
    """
    Executes a WorkerCommand.

    This function is a part of a multiple dispatch system, meaning it will only be called
    if the argument is of type WorkerCommand.

    Args:
        cmd (WorkerCommand): The command to execute.
        type_converter (Optional[TypeConverter]): An optional TypeConverter to use during execution.

    Returns:
        Any: The result of the command execution.
    """
    ...
