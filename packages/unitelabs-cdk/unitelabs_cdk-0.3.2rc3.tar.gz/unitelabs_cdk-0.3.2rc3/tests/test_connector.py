import os
import unittest.mock

import pytest

from sila import discovery
from unitelabs.cdk.connector import Connector


@pytest.fixture
def no_broadcast(monkeypatch):
    class FakeBroadcaster(discovery.Broadcaster):
        """Fake Broadcaster."""

        def __init__(self, *args, **kwargs):
            self.start = unittest.mock.AsyncMock()
            self.stop = unittest.mock.AsyncMock()

    monkeypatch.setattr(discovery, "Broadcaster", FakeBroadcaster)


class TestConnector:
    # Create a new connector with default values
    async def test_create_new_connector_with_default_values(self, no_broadcast):
        connector = Connector()

        assert connector.config.environment == "development"

    async def test_config_uses_envvars(self, no_broadcast):
        os.environ["SILA_SERVER__TLS"] = "true"

        cert = "./cert.pem"
        key = "./key.pem"
        os.environ["SILA_SERVER__CERT"] = cert
        os.environ["SILA_SERVER__KEY"] = key

        connector = Connector()

        assert connector.config.sila_server["tls"] == True
        assert connector.config.sila_server["cert"] == cert.encode("ascii")
        assert connector.config.sila_server["key"] == key.encode("ascii")


class TestStart:
    # The start method calls close after cancellation
    async def test_start_calls_close_on_cancellation(self, no_broadcast):
        with (
            unittest.mock.patch("sila.server.Server", spec=True),
            unittest.mock.patch("sila.discovery.Broadcaster", spec=True),
            unittest.mock.patch("sila.cloud_connector.CloudServerEndpoint", spec=True),
        ):
            connector = Connector()
            connector.close = unittest.mock.AsyncMock()

            await connector.start()

            connector.close.assert_awaited_once_with()


class TestClose:
    # The close method calls shutdown handlers
    async def test_close_calls_shutdown_handlers(self, no_broadcast):
        with (
            unittest.mock.patch("sila.server.Server", spec=True),
            unittest.mock.patch("sila.discovery.Broadcaster", spec=True),
            unittest.mock.patch("sila.cloud_connector.CloudServerEndpoint", spec=True),
        ):
            handler = unittest.mock.Mock()
            connector = Connector()
            connector.on_shutdown(handler=handler)

            await connector.close()

            handler.assert_called_once_with()

    # The close method calls shutdown handlers in order of registration
    async def test_close_calls_shutdown_handlers_in_order(self, no_broadcast):
        with (
            unittest.mock.patch("sila.server.Server", spec=True),
            unittest.mock.patch("sila.discovery.Broadcaster", spec=True),
            unittest.mock.patch("sila.cloud_connector.CloudServerEndpoint", spec=True),
        ):
            handler = unittest.mock.Mock()
            handler.handler_1 = unittest.mock.Mock()
            handler.handler_2 = unittest.mock.Mock()
            connector = Connector()
            connector.on_shutdown(handler=handler.handler_1)
            connector.on_shutdown(handler=handler.handler_2)

            await connector.close()

            handler.assert_has_calls([unittest.mock.call.handler_1(), unittest.mock.call.handler_2()])

    # The close method calls async shutdown handlers
    async def test_close_calls_async_shutdown(self, no_broadcast):
        with (
            unittest.mock.patch("sila.server.Server", spec=True),
            unittest.mock.patch("sila.discovery.Broadcaster", spec=True),
            unittest.mock.patch("sila.cloud_connector.CloudServerEndpoint", spec=True),
        ):
            handler = unittest.mock.AsyncMock()
            connector = Connector()
            connector.on_shutdown(handler=handler)

            await connector.start()

            handler.assert_awaited_once_with()

    # The close method ignores exception in shutdown handlers
    async def test_close_ignores_exception_in_shutdown(self, no_broadcast):
        with (
            unittest.mock.patch("sila.server.Server", spec=True),
            unittest.mock.patch("sila.discovery.Broadcaster", spec=True),
            unittest.mock.patch("sila.cloud_connector.CloudServerEndpoint", spec=True),
        ):
            handler_1 = unittest.mock.Mock(side_effect=RuntimeError)
            handler_2 = unittest.mock.AsyncMock(side_effect=RuntimeError)
            connector = Connector()
            connector.on_shutdown(handler=handler_1)
            connector.on_shutdown(handler=handler_2)

            await connector.start()

            handler_1.assert_called_once_with()
            handler_2.assert_awaited_once_with()


class TestOnShutdown:
    # Can add a shutdown handler to the list of handlers
    async def test_add_shutdown_handler(self, no_broadcast):
        connector = Connector()

        def shutdown_handler():
            print("Shutdown handler called")

        connector.on_shutdown(shutdown_handler)

        assert len(connector._shutdown_handlers) == 1
        assert connector._shutdown_handlers[0] == shutdown_handler

    # Adding a shutdown handler with a non-callable object raises a TypeError
    async def test_add_non_callable_handler_raises_type_error(self, no_broadcast):
        connector = Connector()
        non_callable_handler = "not a callable object"

        with pytest.raises(TypeError, match=r"The `handler` argument must be callable."):
            connector.on_shutdown(
                non_callable_handler,  # type: ignore
            )


class TestOffShutdown:
    # Can remove a previously added shutdown hook
    async def test_remove_shutdown_hook(self, no_broadcast):
        # Initialize the class object
        connector = Connector()

        # Define a mock handler
        mock_handler = unittest.mock.Mock()

        # Add the mock handler to the shutdown handlers list
        connector.on_shutdown(mock_handler)

        # Remove the mock handler using off_shutdown method
        connector.off_shutdown(mock_handler)

        # Assert that the mock handler is no longer in the shutdown handlers list
        assert mock_handler not in connector._shutdown_handlers

    # removing a shutdown hook from an empty list of shutdown handlers
    async def test_remove_shutdown_hook_from_empty_list(self, no_broadcast):
        # Initialize the class object
        connector = Connector()

        # Define a mock handler
        mock_handler = unittest.mock.Mock()

        # Remove the mock handler using off_shutdown method
        connector.off_shutdown(mock_handler)

        # Assert that the mock handler is still not in the shutdown handlers list
        assert mock_handler not in connector._shutdown_handlers
