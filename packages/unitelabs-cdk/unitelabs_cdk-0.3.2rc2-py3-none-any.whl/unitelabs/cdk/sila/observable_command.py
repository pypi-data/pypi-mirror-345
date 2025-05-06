import collections.abc
import dataclasses
import functools
import inspect
import typing

import sila.server as sila

from . import utils
from .commands import IntermediateResponses, Parameters, Responses
from .commands.intermediate import Intermediate
from .commands.status import Status
from .defined_execution_error import define_error


@dataclasses.dataclass
class ObservableCommand:
    """A SiLA Observable Command."""

    name: str = ""
    description: str = ""
    errors: list[type[Exception]] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.parameter_by_identifier = {}
        self.responses = sila.data_types.Structure()
        self.intermediate_responses = sila.data_types.Structure()

    def __call__(self, function: collections.abc.Callable) -> collections.abc.Callable:  # noqa: D102
        setattr(function, "__handler", self)
        return function

    def attach(self, feature: sila.Feature, function: collections.abc.Callable) -> sila.ObservableCommand:
        """
        Create and attach a `sila.ObservableCommand` to the `feature`.

        Args:
          feature: The `Feature` to which the command will be attached.
          function: The underlying callable executed by the command.

        Returns:
          The command instance which was attached to the `Feature`.
        """
        docs = utils.parse_docs(inspect.getdoc(function))

        display_name = self.name or utils.humanize(function.__name__)
        identifier = display_name.replace(" ", "")
        description = self.description or docs.get("default", "")

        parameters = Parameters.from_signature(feature, function)
        self.responses = Responses.from_signature(feature, function)
        self.intermediate_responses = IntermediateResponses.from_signature(feature, function)
        self.parameter_by_identifier = parameters.get_mapping(function)

        observable_command = sila.ObservableCommand(
            identifier=identifier,
            display_name=display_name,
            description=description,
            function=functools.partial(self.execute, function),
            errors=[define_error(error) for error in self.errors],
            parameters=parameters,
            responses=self.responses,
            intermediate_responses=self.intermediate_responses,
        )
        feature.add_handler(observable_command)

        return observable_command

    async def execute(self, function: collections.abc.Callable, **kwargs):  # noqa: ANN201
        """
        Execute a given function with the provided keyword arguments.

        Args:
          function: The function to be executed.
          **kwargs: Additional keyword arguments to be passed to the function.

        Returns:
          The result of the function execution.

        Raises:
          DefinedExecutionError: If the error type is in the list of defined errors.
          Exception: If an unexpected error occurs during execution.
        """

        try:
            parameters = self.parse_parameters(kwargs)
            responses = function(**parameters)
            if inspect.isawaitable(responses):
                responses = await responses

            return self.parse_responses(responses)
        except Exception as error:
            if type(error) in self.errors:
                raise define_error(error) from None

            raise error

    def parse_parameters(self, parameters: dict) -> dict:
        """
        Parse parameter values.

        Args:
          parameters: The parameters to be parsed.

        Returns:
          The parsed parameters, structured into a dictionary.
        """
        command_execution = parameters.pop("command_execution", {})

        result = {}
        for key, parameter in parameters.items():
            key = self.parameter_by_identifier.get(key, key)  # noqa: PLW2901
            result[key] = parameter

        if command_execution:
            result["status"] = Status(command_execution=command_execution)
            if len(self.intermediate_responses.elements):
                result["intermediate"] = Intermediate(command_execution=command_execution)

        return result

    def parse_responses(self, responses: typing.Optional[typing.Union[tuple, list]]) -> dict:
        """
        Parse response values.

        Args:
          responses: The responses to be parsed.

        Returns:
          The parsed responses, structured into a dictionary, or an empty dictionary if no responses are provided.
        """
        if responses is None:
            return {}

        result = {}
        responses = [responses] if not isinstance(responses, tuple) else responses
        for index, response in enumerate(responses):
            key = self.responses.elements[index].identifier if index < len(self.responses.elements) else index
            result[key] = response

        return result
