import asyncio
import contextlib
import time
import typing

from .sila.utils import clear_interval, set_interval

T = typing.TypeVar("T")


class Publisher(typing.Generic[T]):
    """
    Manage subscriptions with an optional data source.

    Args:
      maxsize: The maximum number of messages to track in the queue.
      default: The default value of the subscription.
      source: An awaitable method that can be called at a fixed interval as the data source of the subscription.

    Examples:
      Creat a publisher and set a temporary source for subscriptions:
      >>> publisher = Publisher[str](maxsize=100)
      >>> publisher.set(method, interval=2)
      >>> async for state in publisher.subscribe():
      >>>     yield state

      Create a publisher with a stable source:
      >>> publisher = Publisher[str](maxsize=100, source=method, interval=2)
      >>> async for state in publisher.subscribe():
      >>>     yield state

    """

    def __init__(
        self,
        maxsize: int = 0,
        default: typing.Optional[T] = None,
        source: typing.Optional[typing.Callable[[], typing.Awaitable[T]]] = None,
        interval: float = 5,
    ) -> None:
        self._maxsize = maxsize
        self._value: typing.Optional[T] = default
        self.subscribers: list[asyncio.Queue[T]] = []
        self._queue_tasks: set[asyncio.Task] = set()
        # self-updating subscription
        self._setter: typing.Optional[typing.Callable[[], typing.Awaitable[T]]] = None
        self._update_task: typing.Optional[asyncio.Task] = None
        self._source = source
        self._interval = interval

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

    def set(
        self,
        setter: typing.Callable[[], typing.Awaitable[T]],
        interval: float = 5,
    ) -> None:
        """
        Create a temporary background task to poll data from an awaitable method and update `Publisher`.

        Task will be destroyed when all subscriptions to the `Publisher` are removed.

        Args:
          setter: The awaitable called at a fixed interval to update the current value of the `Publisher`.
          interval: The amount of time in seconds to wait between polling calls to `setter`.
        """
        self._setter = setter
        self._update_task = set_interval(self.__self_update, delay=interval)

    async def __self_update(self) -> None:
        if self._setter:
            new_value = await self._setter()
            self.update(new_value)

    async def subscribe(self, abort: typing.Optional[asyncio.Event] = None) -> typing.AsyncIterator[T]:
        """
        Subscribe to updates from this Publisher.

        Args:
          abort: An cancellable event, allowing subscriptions to be terminated.

        Examples:
          Set and subscribe to a publisher with a temporary source:
          >>> publisher = Publisher[str](maxsize=100)
          >>> publisher.set(method, interval=2)
          >>> async for state in publisher.subscribe():
          >>>     yield state

          Subscribe to a publisher with a stable source:
          >>> publisher = Publisher[str](maxsize=100, source=method, interval=2)
          >>> async for state in publisher.subscribe():
          >>>     yield state
        """
        queue = self.add()

        abort = abort or asyncio.Event()
        cancellation = asyncio.create_task(abort.wait())

        if self._source and not self._update_task:
            self.set(self._source, self._interval)
        try:
            while not abort.is_set():
                queue_task = asyncio.create_task(queue.get())
                self._queue_tasks.add(queue_task)
                queue_task.add_done_callback(self._queue_tasks.discard)

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
        """Update the current value of this `Publisher`, if `value` is not current value."""
        if self._value != value:
            self._value = value
            self.notify()

    def add(self) -> asyncio.Queue:
        """Add a subscriber to this `Publisher`."""
        queue = asyncio.Queue[T]()
        if self._value is not None:
            queue.put_nowait(self._value)

        self.subscribers.append(queue)

        return queue

    def remove(self, subscriber: asyncio.Queue) -> None:
        """Remove a subscriber from this `Publisher`."""
        self.subscribers.remove(subscriber)

        if not self.subscribers:
            for task in self._queue_tasks:
                task.cancel()

            if self._update_task:
                clear_interval(self._update_task)
                self._update_task = None
                self._setter = None
