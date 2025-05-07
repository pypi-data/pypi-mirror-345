import unittest.mock

import pytest

from sila.errors.defined_execution_error import DefinedExecutionError
from unitelabs.cdk.sila.observable_command import ObservableCommand
from unitelabs.cdk.sila.unobservable_command import UnobservableCommand
from unitelabs.cdk.sila.unobservable_property import UnobservableProperty


class DefinedError(Exception):
    pass


@pytest.mark.parametrize(
    "decorator,returns", [(ObservableCommand, dict), (UnobservableCommand, dict), (UnobservableProperty, None)]
)
class TestExecute:
    # Execute synchronous function with default parameters.
    async def test_execute_synchronous_default_parameters(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.Mock(return_value=object())

        # Execute function
        result = await decorator.execute(function=function)

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with()

        # Assert that the method returns the correct value
        expected = {0: function.return_value} if returns is dict else function.return_value
        assert result == expected

    # Execute synchronous function with custom parameters.
    async def test_execute_synchronous_custom_parameters(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.Mock(return_value=object())

        # Execute function
        result = await decorator.execute(function=function, argument="World, World!")

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with(argument="World, World!")

        # Assert that the method returns the correct value
        expected = {0: function.return_value} if returns is dict else function.return_value
        assert result == expected

    # Execute synchronous function with no return value.
    async def test_execute_synchronous_returns_none(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.Mock(return_value=None)

        # Execute function
        result = await decorator.execute(function=function, argument="World, World!")

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with(argument="World, World!")

        # Assert that the method returns the correct value
        expected = {} if returns is dict else None
        assert result == expected

    # Verify that the method raises an error when the synchronous function raises.
    async def test_raises_when_synchronous_raises(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.Mock(side_effect=Exception("Hello, World!"))

        # Execute function
        with pytest.raises(Exception, match=r"Hello, World!"):
            await decorator.execute(function=function)

    # Verify that the method raises a defined execution error when the synchronous decorator knows the error type.
    async def test_raises_when_synchronous_raises_known_error(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator(errors=[DefinedError])
        function = unittest.mock.Mock(side_effect=DefinedError("Hello, World!"))

        # Execute function
        with pytest.raises(DefinedExecutionError) as exc_info:
            await decorator.execute(function=function)

        assert exc_info.value.identifier == "DefinedError"
        assert exc_info.value.display_name == "Defined Error"
        assert exc_info.value.description == "Hello, World!"

    # Execute asynchronous function with default parameters.
    async def test_execute_asynchronous_default_parameters(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.AsyncMock(return_value=object())

        # Execute function
        result = await decorator.execute(function=function)

        # Assert that the function was called with the correct arguments
        function.assert_awaited_once_with()

        # Assert that the method returns the correct value
        expected = {0: function.return_value} if returns is dict else function.return_value
        assert result == expected

    # Execute asynchronous function with custom parameters.
    async def test_execute_asynchronous_custom_parameters(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.AsyncMock(return_value=object())

        # Execute function
        result = await decorator.execute(function=function, argument="World, World!")

        # Assert that the function was called with the correct arguments
        function.assert_awaited_once_with(argument="World, World!")

        # Assert that the method returns the correct value
        expected = {0: function.return_value} if returns is dict else function.return_value
        assert result == expected

    # Execute asynchronous function with no return value.
    async def test_execute_asynchronous_returns_none(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.AsyncMock(return_value=None)

        # Execute function
        result = await decorator.execute(function=function, argument="World, World!")

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with(argument="World, World!")

        # Assert that the method returns the correct value
        expected = {} if returns is dict else None
        assert result == expected

    # Verify that the method raises an error when the asynchronous function raises.
    async def test_raises_when_asynchronous_raises(self, decorator, returns):
        # Initialize the unobservable command
        decorator = decorator()
        function = unittest.mock.AsyncMock(side_effect=Exception("Hello, World!"))

        # Execute function
        with pytest.raises(Exception, match=r"Hello, World!"):
            await decorator.execute(function=function)

    # Verify that the method raises a defined execution error when the asynchronous decorator knows the error type.
    async def test_raises_when_asynchronous_raises_known_error(self, decorator, returns):
        # Initialize the unobservable command
        decorator = ObservableCommand(errors=[DefinedError])
        function = unittest.mock.AsyncMock(side_effect=DefinedError("Hello, World!"))

        # Execute function
        with pytest.raises(DefinedExecutionError) as exc_info:
            await decorator.execute(function=function)

        assert exc_info.value.identifier == "DefinedError"
        assert exc_info.value.display_name == "Defined Error"
        assert exc_info.value.description == "Hello, World!"
