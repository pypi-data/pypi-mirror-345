import asyncio
import contextlib
import time
import typing

T = typing.TypeVar("T")


from .sila.utils import clear_interval, set_interval


class Publisher(typing.Generic[T]):
    """
    A publisher which exposes an interface for subscriptions.

    Args:
      maxsize: The maximum number of messages to track in the queue.
      default: The default value of the subscription.
    """

    def __init__(
        self,
        maxsize: int = 0,
        default: typing.Optional[T] = None,
    ) -> None:
        self._maxsize = maxsize
        self._value: typing.Optional[T] = default
        self.subscribers: list[asyncio.Queue[T]] = []
        self._update: typing.Optional[typing.Callable[[], typing.Awaitable[T]]] = None
        self.subscription: typing.Optional[asyncio.Task] = None

    @property
    def current(self) -> typing.Optional[T]:
        """The current value."""
        return self._value

    async def get(
        self,
        predicate: typing.Callable[[T], bool] = lambda _: True,
        timeout: typing.Optional[float] = None,
        current: bool = False,
    ) -> T:
        """
        Request an upcoming event that satisfies the predicate.

        Args:
          predicate: A filter predicate to apply.
          timeout: How many seconds to wait for new value.
          current: Whether to check the current value against the predicate.

        Raises:
          TimeoutError
        """

        queue = self.add()
        start_time = time.perf_counter()

        if current and (value := self.current) and predicate(value):
            return value

        try:
            while True:
                wait_for = timeout + start_time - time.perf_counter() if timeout is not None else None

                try:
                    value = await asyncio.wait_for(queue.get(), timeout=wait_for)
                    queue.task_done()
                except (TimeoutError, asyncio.TimeoutError):
                    raise TimeoutError from None

                if predicate(value):
                    return value
        finally:
            self.remove(queue)

    async def set(self, subscription_method: typing.Callable[[], typing.Awaitable[T]], interval: float = 5) -> None:
        """
        Set the publisher to poll data at a fixed interval from a awaitable method.

        Args:
          subscription_method: The awaitable to called at a fixed interval to set the current value of the publisher.
          interval: The amount of time in seconds to wait between calls to `subscription_method`.
        """
        self._update = subscription_method
        self.subscription = set_interval(self.__self_update, delay=interval)

    async def __self_update(self) -> None:
        if self._update:
            new_value = await self._update()
            self.update(new_value)

    async def subscribe(self, abort: typing.Optional[asyncio.Event] = None) -> typing.AsyncIterator[T]:
        """
        Subscribe to updates from this Publisher.

        Args:
          abort: An cancellable event, allowing subscriptions to be terminated.

        Examples:
          >>> publisher = Publisher[str](maxsize=100)
          >>> if (current_state:=await self.get_state()) != publisher.current:
          >>>     publisher.update(current_state)
          >>> async for state in publisher.subscribe():
          >>>     yield state
        """
        queue = self.add()

        abort = abort or asyncio.Event()
        cancellation = asyncio.create_task(abort.wait())
        try:
            while not abort.is_set():
                queue_task = asyncio.create_task(queue.get())
                done, pending = await asyncio.wait((queue_task, cancellation), return_when=asyncio.FIRST_COMPLETED)

                if queue_task in done:
                    value = queue_task.result()
                    yield value

                if cancellation in done:
                    for pending_task in pending:
                        with contextlib.suppress(asyncio.TimeoutError):
                            await asyncio.wait_for(pending_task, 0)
                    break

        except asyncio.CancelledError:
            cancellation.cancel()
        finally:
            self.remove(queue)

    def notify(self) -> None:
        """Propagate updates to the current value to all subscribers."""
        if self._value is not None:
            for subscriber in self.subscribers:
                subscriber.put_nowait(self._value)

    def update(self, value: T) -> None:
        """Update the current value of this Publisher."""
        if self._value != value:
            self._value = value
            self.notify()

    def add(self) -> asyncio.Queue:
        """Add a subscriber to this Publisher."""
        queue = asyncio.Queue[T]()
        if self._value is not None:
            queue.put_nowait(self._value)

        self.subscribers.append(queue)

        return queue

    def remove(self, subscriber: asyncio.Queue) -> None:
        """Remove a subscriber from this Publisher."""
        self.subscribers.remove(subscriber)

        if not self.subscribers and self.subscription:
            clear_interval(self.subscription)
            self.subscription = None
            self._update = None
