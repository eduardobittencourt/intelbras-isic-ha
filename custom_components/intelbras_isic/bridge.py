"""Lifecycle for the independently written Python iSIC transport."""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime

from .const import P2P_SERVER, P2P_SERVER_PORT
from .transport.client import Configuration, LoopbackProxy, Transport


class BridgeError(Exception):
    """The P2P transport could not be started."""


class BridgeManager:
    """Own one Python P2P session and loopback proxy per iSIC device."""

    def __init__(
        self, serial: str, remote_port: int, *, application_key: str, p2p_password: str
    ) -> None:
        self.serial = serial
        self.remote_port = remote_port
        self._application_key = application_key
        self._p2p_password = p2p_password
        self.local_port: int | None = None
        self._transport: Transport | None = None
        self._proxy: LoopbackProxy | None = None
        self._lock = asyncio.Lock()
        self.started_at: datetime | None = None
        self._started_monotonic: float | None = None
        self.successful_starts = 0
        self.last_error: str | None = None

    @property
    def ready(self) -> bool:
        """Report peer worker and proxy health, independent of host architecture."""
        return (
            self.local_port is not None
            and self._transport is not None
            and self._transport.alive
            and self._proxy is not None
            and self._proxy.alive
        )

    @property
    def uptime_seconds(self) -> int | None:
        if not self.ready or self._started_monotonic is None:
            return None
        return max(0, int(time.monotonic() - self._started_monotonic))

    @staticmethod
    def _open(transport: Transport) -> LoopbackProxy | Exception:
        # Return thread failures as values. Home Assistant observes shielded
        # task errors even when the cancelled caller subsequently retrieves them.
        try:
            transport.connect()
            return LoopbackProxy(transport)
        except Exception as err:
            return err

    async def async_start(self) -> int:
        """Establish a session without blocking Home Assistant's event loop."""
        async with self._lock:
            if self.ready:
                assert self.local_port is not None
                return self.local_port
            await self._async_stop_locked()
            transport = Transport(
                Configuration(
                    P2P_SERVER,
                    P2P_SERVER_PORT,
                    self._application_key,
                    self._p2p_password,
                    self.serial,
                    self.remote_port,
                )
            )
            task = asyncio.create_task(asyncio.to_thread(self._open, transport))
            try:
                proxy = await asyncio.shield(task)
                if isinstance(proxy, Exception):
                    raise proxy
            except BaseException as err:
                # to_thread keeps running after coroutine cancellation. Close
                # its sockets, then join it and close any late-created proxy.
                await asyncio.to_thread(transport.close)
                outcome = (await asyncio.gather(task, return_exceptions=True))[0]
                if isinstance(outcome, LoopbackProxy):
                    await asyncio.to_thread(outcome.close)
                if isinstance(err, asyncio.CancelledError):
                    raise
                self.last_error = "Unable to establish the iSIC P2P session"
                raise BridgeError(self.last_error) from None
            self._transport = transport
            self._proxy = proxy
            self.local_port = proxy.port
            self.started_at = datetime.now(UTC)
            self._started_monotonic = time.monotonic()
            self.successful_starts += 1
            self.last_error = None
            return proxy.port

    async def async_stop(self) -> None:
        async with self._lock:
            await self._async_stop_locked()

    async def _async_stop_locked(self) -> None:
        proxy, transport = self._proxy, self._transport
        self._proxy = None
        self._transport = None
        self.local_port = None
        self.started_at = None
        self._started_monotonic = None

        def close() -> None:
            if proxy is not None:
                proxy.close()
            if transport is not None:
                transport.close()

        await asyncio.to_thread(close)
