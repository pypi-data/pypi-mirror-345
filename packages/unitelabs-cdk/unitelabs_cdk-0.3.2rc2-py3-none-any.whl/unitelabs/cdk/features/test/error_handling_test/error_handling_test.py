from unitelabs.cdk import sila


class TestError(Exception):
    """An error exclusively used for testing purposes."""


class ErrorHandlingTest(sila.Feature):
    """Tests that errors are propagated correctly."""

    def __init__(self):
        super().__init__(
            originator="org.silastandard",
            category="test",
            version="1.0",
        )

    @sila.UnobservableCommand(errors=[TestError])
    async def raise_defined_execution_error(self) -> None:
        """Raise the "Test Error" with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise TestError(msg)

    @sila.ObservableCommand(errors=[TestError])
    async def raise_defined_execution_error_observably(self, *, status: sila.Status) -> None:  # noqa: ARG002
        """Raise the "Test Error" with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise TestError(msg)

    @sila.UnobservableCommand()
    async def raise_undefined_execution_error(self) -> None:
        """Raise an Undefined Execution Error with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise RuntimeError(msg)

    @sila.ObservableCommand()
    async def raise_undefined_execution_error_observably(self, *, status: sila.Status) -> None:  # noqa: ARG002
        """Raise an Undefined Execution Error with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise RuntimeError(msg)

    @sila.UnobservableProperty(errors=[TestError])
    async def raise_defined_execution_error_on_get(self) -> int:
        """Raise a "Test Error" from on property get with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise TestError(msg)

    @sila.ObservableProperty(errors=[TestError])
    async def raise_defined_execution_error_on_subscribe(self) -> sila.Stream[int]:
        """Raise a "Test Error" on subscription to property with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise TestError(msg)

    @sila.UnobservableProperty()
    async def raise_undefined_execution_error_on_get(self) -> int:
        """Raise an Undefined Execution Error on property get with the error message 'SiLA2_test_error_message'."""

        msg = "SiLA2_test_error_message"
        raise RuntimeError(msg)

    @sila.ObservableProperty()
    async def raise_undefined_execution_error_on_subscribe(self) -> sila.Stream[int]:
        """
        Raise an Undefined Execution Error on subscription to property.

        The raised error contains the error message 'SiLA2_test_error_message'.
        """

        msg = "SiLA2_test_error_message"
        raise RuntimeError(msg)

    @sila.ObservableProperty(errors=[TestError])
    async def raise_defined_execution_error_after_value_was_sent(self) -> sila.Stream[int]:
        """
        Send the integer value 1 and then raise a Defined Execution Error.

        The raised error contains the error message 'SiLA2_test_error_message'.
        """

        yield 1

        msg = "SiLA2_test_error_message"
        raise TestError(msg)

    @sila.ObservableProperty()
    async def raise_undefined_execution_error_after_value_was_sent(self) -> sila.Stream[int]:
        """
        Send the integer value 1 and then raise a Undefined Execution Error.

        The raised error contains the error message 'SiLA2_test_error_message'.
        """

        yield 1

        msg = "SiLA2_test_error_message"
        raise RuntimeError(msg)
