from talkomatic.dataclasses import User

import argparse
from shlex import split as split_args
from typing import Callable, Awaitable, Any, Type, Union



class _ArgumentParser(argparse.ArgumentParser):
    """
    A private class that is identical to argparse.ArgumentParser, the
    only change being that error messages are not printed.
    """

    def error(self, message: str) -> None:
        pass

class CommandParameter:
    """
    A class that represents a parameter for a command.

    Args:
        name (str): The name of the parameter.
        description (str): The description of the parameter.
        data_type (object): The type of the parameter.
        aliases (list[str]): The aliases of the parameter.
        required (bool): Whether the parameter is required.
        number_of_args (int): The number of arguments the parameter can take. (INFINITE_ARGS for infinite)
    """

    name: str
    description: str
    data_type: Type[Union[int, float, str, bool]]
    aliases: list[str]
    positional: bool
    required: bool
    number_of_args: int

    def __init__(self, name: str, description: str, data_type: Type[Union[int, float, str, bool]], positional: bool = False, aliases: list[str] = [], required: bool = True, number_of_args: int = 1) -> None:
        if data_type not in (int, float, str, bool):
            raise ValueError("Invalid data type")
        
        self.name = name
        self.description = description
        self.data_type = data_type
        self.positional = positional
        self.aliases = aliases
        self.required = required
        self.number_of_args = number_of_args

class Command:
    function: Callable[..., Awaitable[Any]]
    _parser: argparse.ArgumentParser
    name: str
    description: str
    aliases: list[str]
    parameters: list[CommandParameter]
    hidden: bool

    def __init__(self, name: str, description: str, aliases: list[str] = [], hidden: bool = False) -> None:
        self.name = name
        self.description = description
        self.aliases = aliases
        self.hidden = hidden
        self._parser = _ArgumentParser(prog = name, description = description, add_help = False)
    
    def add_argument(self, names: list[str], description: str, data_type: Type[Union[int, float, str, bool]], positional: bool = False, required: bool = True, number_of_args: int = 1) -> None:
        required_args = {}
        if positional:
            if required:
                if number_of_args == INFINITE_ARGS:
                    required_args["nargs"] = "+"
                else:
                    required_args["nargs"] = number_of_args
            elif number_of_args == INFINITE_ARGS:
                required_args["nargs"] = "*"
            else:
                required_args["nargs"] = "?"
        else:
            if required:
                required_args["required"] = True
        self._parser.add_argument(*[f"{'--' if not positional else ''}{name}" for name in names], help = description, type = data_type, **required_args)
    
    async def execute(self, user: User, args: str) -> str:
        try:
            try:
                namespace = self._parser.parse_args(split_args(args))
            except SystemExit:
                return ""

            await self.function(user, **vars(namespace))
            return ""
        except Exception as e:
            return f"Internal bot error: {str(e)}"

INFINITE_ARGS = -1

__all__ = ["Command", "CommandParameter", "INFINITE_ARGS"]
