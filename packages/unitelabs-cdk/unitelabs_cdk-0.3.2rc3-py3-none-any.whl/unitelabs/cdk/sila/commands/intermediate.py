from __future__ import annotations

import typing
import weakref

from sila.commands import CommandExecution

T = typing.TypeVar("T")


class Intermediate(typing.Generic[T]):
    """A class representing an intermediate response in a command execution."""

    def __init__(self, command_execution: CommandExecution):
        self.command_execution: CommandExecution = weakref.proxy(command_execution)

    def send(self, value: T) -> None:
        """Send an intermediate response."""
        self.command_execution.send_intermediate_responses(value)
