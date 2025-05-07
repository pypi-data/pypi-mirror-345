import asyncio
import collections.abc
import typing
import unittest.mock

import pytest

from sila.errors.defined_execution_error import DefinedExecutionError
from unitelabs.cdk.sila.observable_property import ObservableProperty


class DefinedError(Exception):
    pass


async def arange(stop: typing.SupportsIndex) -> collections.abc.AsyncGenerator[int, None]:
    for i in range(stop):
        yield i
        await asyncio.sleep(0)


class TestExecute:
    # Execute synchronous function with default parameters.
    async def test_execute_synchronous_default_parameters(self):
        # Initialize the unobservable property
        decorator = ObservableProperty()
        return_values = [object(), object(), object()]
        function = unittest.mock.Mock(return_value=(return_values[i] for i in range(3)))

        # Execute function
        result = decorator.execute(function=function)
        result_0 = await result.__anext__()
        result_1 = await result.__anext__()
        result_2 = await result.__anext__()

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with()

        # Assert that the method returns the correct value
        assert result_0 == return_values[0]
        assert result_1 == return_values[1]
        assert result_2 == return_values[2]

    # Execute synchronous function with custom parameters.
    async def test_execute_synchronous_custom_parameters(self):
        # Initialize the unobservable property
        decorator = ObservableProperty()
        return_values = [object(), object(), object()]
        function = unittest.mock.Mock(return_value=(return_values[i] for i in range(3)))

        # Execute function
        result = decorator.execute(function=function, argument="World, World!")
        result_0 = await result.__anext__()
        result_1 = await result.__anext__()
        result_2 = await result.__anext__()

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with(argument="World, World!")

        # Assert that the method returns the correct value
        assert result_0 == return_values[0]
        assert result_1 == return_values[1]
        assert result_2 == return_values[2]

    # Verify that the method raises an error when the synchronous function raises.
    async def test_raises_when_synchronous_raises(self):
        # Initialize the unobservable property
        decorator = ObservableProperty()
        function = unittest.mock.Mock(side_effect=Exception("Hello, World!"))

        # Execute function
        result = decorator.execute(function=function)
        with pytest.raises(Exception, match=r"Hello, World!"):
            await result.__anext__()

    # Verify that the method raises a defined execution error when the synchronous decorator knows the error type.
    async def test_raises_when_synchronous_raises_known_error(self):
        # Initialize the unobservable property
        decorator = ObservableProperty(errors=[DefinedError])
        function = unittest.mock.Mock(side_effect=DefinedError("Hello, World!"))

        # Execute function
        result = decorator.execute(function=function)
        with pytest.raises(DefinedExecutionError) as exc_info:
            await result.__anext__()

        assert exc_info.value.identifier == "DefinedError"
        assert exc_info.value.display_name == "Defined Error"
        assert exc_info.value.description == "Hello, World!"

    # Execute asynchronous function with default parameters.
    async def test_execute_asynchronous_default_parameters(self):
        # Initialize the unobservable property
        decorator = ObservableProperty()
        return_values = [object(), object(), object()]
        function = unittest.mock.AsyncMock(return_value=(return_values[i] async for i in arange(3)))

        # Execute function
        result = decorator.execute(function=function)
        result_0 = await result.__anext__()
        result_1 = await result.__anext__()
        result_2 = await result.__anext__()

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with()

        # Assert that the method returns the correct value
        assert result_0 == return_values[0]
        assert result_1 == return_values[1]
        assert result_2 == return_values[2]

    # Execute synchronous function with custom parameters.
    async def test_execute_asynchronous_custom_parameters(self):
        # Initialize the unobservable property
        decorator = ObservableProperty()
        return_values = [object(), object(), object()]
        function = unittest.mock.AsyncMock(return_value=(return_values[i] async for i in arange(3)))

        # Execute function
        result = decorator.execute(function=function, argument="World, World!")
        result_0 = await result.__anext__()
        result_1 = await result.__anext__()
        result_2 = await result.__anext__()

        # Assert that the function was called with the correct arguments
        function.assert_called_once_with(argument="World, World!")

        # Assert that the method returns the correct value
        assert result_0 == return_values[0]
        assert result_1 == return_values[1]
        assert result_2 == return_values[2]

    # Verify that the method raises an error when the asynchronous function raises.
    async def test_raises_when_asynchronous_raises(self):
        # Initialize the unobservable property
        decorator = ObservableProperty()
        function = unittest.mock.AsyncMock(side_effect=Exception("Hello, World!"))

        # Execute function
        result = decorator.execute(function=function)
        with pytest.raises(Exception, match=r"Hello, World!"):
            await result.__anext__()

    # Verify that the method raises a defined execution error when the asynchronous decorator knows the error type.
    async def test_raises_when_asynchronous_raises_known_error(self):
        # Initialize the unobservable property
        decorator = ObservableProperty(errors=[DefinedError])
        function = unittest.mock.AsyncMock(side_effect=DefinedError("Hello, World!"))

        # Execute function
        result = decorator.execute(function=function)
        with pytest.raises(DefinedExecutionError) as exc_info:
            await result.__anext__()

        assert exc_info.value.identifier == "DefinedError"
        assert exc_info.value.display_name == "Defined Error"
        assert exc_info.value.description == "Hello, World!"
