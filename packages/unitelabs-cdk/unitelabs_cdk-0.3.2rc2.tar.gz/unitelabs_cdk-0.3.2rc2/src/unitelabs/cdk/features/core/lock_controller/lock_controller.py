from __future__ import annotations

import asyncio
import dataclasses
from collections.abc import AsyncIterator

import typing_extensions as typing

from unitelabs.cdk import sila

from .lock_controller_base import InvalidLockIdentifier, LockControllerBase, ServerAlreadyLocked, ServerNotLocked


@dataclasses.dataclass
class Lock:
    """A lock on a SiLA Server."""

    identifier: str
    timeout: sila.datetime.timedelta
    last_usage: sila.datetime.datetime = dataclasses.field(default_factory=sila.datetime.datetime.now)

    @property
    def expired(self) -> bool:
        """Whether the lock has expired."""
        return (sila.datetime.datetime.now() - self.timeout) > self.last_usage


class LockController(LockControllerBase):
    """Lock a SiLA Server for exclusive use, preventing other SiLA Clients from using it."""

    def __init__(self, affects: list[sila.identifiers.FullyQualifiedIdentifier] | None = None):
        super().__init__()

        self.affects = affects
        self._lock: typing.Optional[Lock] = None
        self._event = asyncio.Event()

    @property
    def lock(self) -> typing.Optional[Lock]:
        """The lock on the SiLA Server, if any."""
        if self._lock and self._lock.expired:
            self._event.set()
            self._lock = None

        return self._lock

    @lock.setter
    def lock(self, value: typing.Optional[Lock]) -> None:
        self._event.set()
        self._lock = value

    @typing.override
    async def subscribe_is_locked(self) -> AsyncIterator[bool]:
        try:
            while True:
                yield self.lock is not None
                await self._event.wait()
                self._event.clear()
        finally:
            pass

    @typing.override
    def lock_server(self, lock_identifier, timeout) -> None:  # noqa: ANN001
        if self.lock:
            raise ServerAlreadyLocked

        self.lock = Lock(identifier=lock_identifier, timeout=sila.datetime.timedelta(seconds=timeout))

    @typing.override
    def unlock_server(self, lock_identifier: str) -> None:
        lock = self.lock
        if lock is None:
            raise ServerNotLocked

        if lock.identifier != lock_identifier:
            raise InvalidLockIdentifier

        self.lock = None

    def add_to_server(self, server: sila.Server) -> None:
        """Add the LockController to a server."""
        self.add_metadata(LockIdentifier(self))
        super().add_to_server(server=server)


class LockIdentifier(sila.Metadata):
    """
    The lock identifier.

    This must be sent with every (lock protected) call in order to use the functionality
    of a locked SiLA Server.
    """

    def __init__(self, lock_controller: LockController):
        super().__init__(data_type=sila.data_types.String(), errors=[InvalidLockIdentifier()])
        self.lock_controller = lock_controller

    def affects(self) -> list[sila.identifiers.FullyQualifiedIdentifier]:
        """Which features are protected by the lock."""
        if not self.lock_controller.server:
            return self.lock_controller.affects or []

        return self.lock_controller.affects or [
            feature.fully_qualified_identifier
            for feature in self.lock_controller.server.features.values()
            if feature.identifier not in ("SiLAService", "LockController")
        ]

    def intercept(self, handler: sila.Handler, metadata_: dict) -> None:
        """
        Intercept a `sila.Handler` to check for a valid lock identifier, reject if invalid.

        Raises:
          FrameworkError: If the required SiLA Client Metadata has not been sent.
          InvalidLockIdentifier: If there is no lock currently active or the provided lock identifier is invalid.
        """
        if any(str(handler.fully_qualified_identifier).startswith(str(affected)) for affected in self.affects()):
            data: bytes | None = metadata_.get(
                "sila-org.silastandard-core-lockcontroller-v2-metadata-lockidentifier-bin"
            )

            if data is None:
                raise sila.errors.FrameworkError(
                    error_type=sila.errors.FrameworkError.Type.INVALID_METADATA,
                    message="The required SiLA Client Metadata has not been sent along or is invalid.",
                )

            identifier: str = self.message.decode(data).get("LockIdentifier", "")

            if not self.lock_controller.lock or self.lock_controller.lock.identifier != identifier:
                raise InvalidLockIdentifier

            self.lock_controller.lock.last_usage = sila.datetime.datetime.now()
