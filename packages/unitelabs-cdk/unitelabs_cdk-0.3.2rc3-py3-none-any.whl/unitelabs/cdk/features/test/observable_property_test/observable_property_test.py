import asyncio

from unitelabs.cdk import sila


class ObservablePropertyTest(sila.Feature):
    """This is a test feature to test observable properties."""

    def __init__(self):
        super().__init__(
            originator="org.silastandard",
            category="test",
            version="1.0",
        )

        self.alternating = True
        self.alternating_event = asyncio.Event()
        sila.utils.set_interval(self._update_alternating, 1)

        self.value: int = 0
        self.value_event = asyncio.Event()

    async def _update_alternating(self) -> None:
        self.alternating = not self.alternating
        self.alternating_event.set()

    @sila.ObservableProperty()
    async def subscribe_fixed_value(self) -> sila.Stream[int]:
        """Return 42."""
        yield 42

    @sila.ObservableProperty()
    async def subscribe_alternating(self) -> sila.Stream[bool]:
        """Switch every second between true and false."""
        while True:
            await self.alternating_event.wait()
            self.alternating_event.clear()
            yield self.alternating

    @sila.ObservableProperty()
    async def subscribe_editable(self) -> sila.Stream[int]:
        """Can be set through SetValue command."""
        while True:
            yield self.value
            await self.value_event.wait()
            self.value_event.clear()

    @sila.UnobservableCommand()
    def set_value(self, value: int) -> None:
        """
        Change the value of Editable.

        .. parameter:: The new value
        """
        self.value = value
        self.value_event.set()
