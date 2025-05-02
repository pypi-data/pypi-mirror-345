
"""
This module provides utilities for setting assembly paths, loading CLR types, and executing commands
in DNV One Workflow.
"""

import importlib
import os
from typing import Any, Optional, Type

import clr
from dnv.oneworkflow.worker_command import WorkerCommand
from multipledispatch import dispatch

from ._type_converter import TypeConverter

ASSEMBLIES_PATH = ""


def set_assembly_path(assemblies_path: str):
    """
    Sets the global variable ASSEMBLIES_PATH to the provided path.

    Args:
        assemblies_path (str): The path to the assemblies.

    Returns:
        None
    """
    global ASSEMBLIES_PATH
    ASSEMBLIES_PATH = assemblies_path


def load_clr_type(type_str: str, use_system_assembly_path: bool = False) -> Type:
    """
    Loads a CLR type from a given type string and optionally uses the system assembly path.

    Args:
        type_str (str): The type string to load the CLR type from. This should be in the format
            'Namespace.ClassName, AssemblyName'.
        use_system_assembly_path (bool, optional): Whether to use the system assembly path. The
            system assembly path is the path where the 'dnv_net_runtime' package finds its system
            DLLs. This is typically a folder named '.dll' located in the same package.
            Defaults to False.

    Returns:
        Type: The loaded CLR type.
    """
    # Split the type string to get the namespace and assembly name
    namespace, assembly = map(str.strip, type_str.split(","))

    # Extract the module name and class name from the namespace
    module_name, class_name = namespace.rsplit(".", 1)

    # Add the reference
    try:
        if use_system_assembly_path:
            clr.AddReference(assembly)
        else:
            clr.AddReference(os.path.join(ASSEMBLIES_PATH, assembly))
    except Exception as e:
        if "Assembly with same name is already loaded" in str(e):
            pass  # Do nothing if the assembly is already loaded
        else:
            print(f"An unexpected issue occurred: {e}")

    # Import the module
    module = importlib.import_module(module_name)

    # Get the class from the module
    class_ = getattr(module, class_name)

    return class_


def create_class_instance_and_set_attributes(
    command: WorkerCommand, type_converter: Optional[TypeConverter] = None
):
    """
    Creates an instance of the class specified by the command's type and sets its attributes.

    Args:
        command (WorkerCommand): The command containing the type and attributes.
        type_converter (TypeConverter, optional): An optional TypeConverter to convert the
            attributes of the command.

    Returns:
        Any: An instance of the class specified by the command's type with its attributes set.
    """
    class_type = load_clr_type(command.type)
    class_instance = class_type()

    converter = TypeConverter() if type_converter is None else type_converter

    attributes = [attr for attr in dir(command) if not attr.startswith("__")]
    for attr in attributes:
        if hasattr(class_instance, attr):
            attr_value = getattr(command, attr)
            if attr_value:
                setattr(class_instance, attr, converter.convert(attr_value))

    return class_instance


def execute_command(
    command: WorkerCommand, type_converter: Optional[TypeConverter] = None
) -> Any:
    """
    Executes a given WorkerCommand. This function loads the 'DNV.One.Workflow.CommandExecution'
    assembly and runs the command. This function is part of a multiple dispatch system and will
    only be called if the argument is of type WorkerCommand.

    Args:
        command (WorkerCommand): The command to be executed.
        type_converter (TypeConverter, optional): An optional TypeConverter to convert the
            attributes of the command. If not provided, a default TypeConverter will be used.

    Returns:
        Any: The result of the command execution.
    """
    class_instance = create_class_instance_and_set_attributes(command, type_converter)

    command_runner_class_type = load_clr_type(
        "DNV.One.Workflow.CommandExecution.CommandRunner, "
        "DNV.One.Workflow.CommandExecution"
    )
    cancellation_token_class_type = load_clr_type(
        "System.Threading.CancellationToken, System.Threading", True
    )

    command_runner = command_runner_class_type()
    attr = getattr(cancellation_token_class_type, "None")
    return command_runner.ExecuteAsync("1", class_instance, attr).Result
