"""
This module contains the TypeConverter class which is used to convert Python types to .NET types.
It supports conversion for basic Python types and allows registration of custom handlers for other
types.
"""

from typing import Any, Callable, Dict, Type

from System.Collections.Generic import (  # pylint: disable=no-name-in-module
    Dictionary,
    List,
)


class TypeConverter:
    """
    A class used to convert Python types to .NET types.

    Attributes:
        custom_handlers (Dict[Type, Callable[[Any], Any]]): A dictionary to store custom handlers
            for types.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the TypeConverter object.
        """
        # Dictionary to store custom handlers
        self.custom_handlers: Dict[Type, Callable[[Any], Any]] = {}

        # Dictionary to store custom handlers
        self.custom_handlers = {list: self.convert_list, dict: self.convert_dict}

    def register_handler(
        self, custom_type: Type, handler: Callable[[Any], Any]
    ) -> None:
        """
        Registers a custom handler for a type.

        Args:
            custom_type (Type): The type for which to register the handler.
            handler (Callable[[Any], Any]): The handler to register for the type.
        """
        self.custom_handlers[custom_type] = handler

    def convert(self, value: Any) -> Any:
        """
        Converts a value to a .NET type using the appropriate handler.

        If a custom handler is registered for the type of the value, it uses that handler for the
        conversion.
        If the value is a list, it converts it to a .NET List.
        If the value is a dictionary, it converts it to a .NET Dictionary.
        If the value is not a list or a dictionary, it returns the value as is.

        Args:
            value (Any): The value to convert.

        Returns:
            Any: The converted value.
        """
        # Convert a value to a .NET type using the appropriate handler
        match type(value):
            case t if t is list:
                # If the value is a list, convert it to a .NET List
                return self.convert_list(value)
            case t if t is dict:
                # If the value is a dictionary, convert it to a .NET Dictionary
                return self.convert_dict(value)
            case t if t in self.custom_handlers:
                # If a custom handler is registered for this type, use it
                return self.custom_handlers[t](value)
            case _:
                # If the value is not a list or a dictionary, return it as is
                return value

    def convert_list(self, value: list[Any]) -> Any:
        """
        Converts a Python list to a .NET List.

        Args:
            value (list[Any]): The Python list to convert.

        Returns:
            List[Any]: The converted .NET List.
        """

        # Determine the type of the first element in the list
        element_type = type(value[0])

        # Create a .NET List of the appropriate type
        net_list = List[element_type]()

        # Add each item in the value list to the .NET List
        for item in value:
            net_list.Add(item)
        return net_list

    def convert_dict(self, value: Dict[Any, Any]) -> Any:
        """
        Converts a Python dictionary to a .NET Dictionary.

        Args:
            value (Dict[Any, Any]): The Python dictionary to convert.

        Returns:
            Dictionary[Any, Any]: The converted .NET Dictionary.
        """

        # Determine the type of the keys and values in the dictionary
        key_type = type(next(iter(value)))
        value_type = type(value[next(iter(value))])

        # Create a .NET Dictionary of the appropriate type
        net_dict = Dictionary[key_type, value_type]()

        # Add each key-value pair in the value dictionary to the .NET Dictionary
        for key, val in value.items():
            net_dict.Add(key, val)

        return net_dict
