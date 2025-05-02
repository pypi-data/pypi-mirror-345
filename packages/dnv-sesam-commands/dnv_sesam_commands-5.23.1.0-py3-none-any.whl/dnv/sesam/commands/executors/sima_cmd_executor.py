"""This module provides functionality for executing SimaCommand."""

import json
from typing import Any

from dnv.oneworkflow.worker_command import WorkerCommand
from multipledispatch import dispatch

# pylint: disable=relative-beyond-top-level
from ..sima_command import SimaCommand
from ._type_converter import TypeConverter
from .command_executor import execute_command as generic_execute_command
from .command_executor import load_clr_type


@dispatch(WorkerCommand)
def execute_command(cmd: WorkerCommand) -> Any:
    """
    Executes a WorkerCommand by loading the 'DNV.One.Workflow.CommandExecution' assembly
    and running the command. This function is part of a multiple dispatch system and will
    only be called if the argument is of type WorkerCommand.

    Args:
        cmd (WorkerCommand): The command to be executed.

    Returns:
        Any: The result of the command execution.
    """
    return generic_execute_command(cmd, type_converter())


def type_converter() -> TypeConverter:
    """
    Initializes a TypeConverter with a custom handler to convert SimaCommand.DataDict instances to
    JObject instances. The handler is registered to the TypeConverter. It works by converting the
    DataDict to a JSON string, then parsing this string to a JObject.

    Returns:
        TypeConverter: The TypeConverter initialized with the custom handler.
    """

    # Import the JObject class from the Newtonsoft.Json.Linq namespace
    jobject_class_type = load_clr_type("Newtonsoft.Json.Linq.JObject, Newtonsoft.Json")

    # Initialize the TypeConverter
    converter = TypeConverter()

    # Define the custom handler
    def convert_dict_to_jobject(value: SimaCommand.DataDict) -> Any:
        return jobject_class_type.Parse(
            json.dumps(value, default=lambda o: o.encode(), indent=4)
        )

    # Register the custom handler
    converter.register_handler(SimaCommand.DataDict, convert_dict_to_jobject)
    return converter
