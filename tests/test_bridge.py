"""Lifecycle, failure cleanup and cancellation of the Python transport adapter."""

import asyncio
import threading
from unittest.mock import MagicMock, patch

import pytest

from custom_components.intelbras_isic.bridge import BridgeError, BridgeManager


async def test_start_is_idempotent_and_dead_worker_is_recreated():
    transport = MagicMock(alive=True)
    proxy = MagicMock(port=45000, alive=True)
    manager = BridgeManager(
        "synthetic-device",
        554,
        application_key="synthetic-key",
        p2p_password="synthetic-password",
    )
    with (
        patch(
            "custom_components.intelbras_isic.bridge.Transport", return_value=transport
        ),
        patch(
            "custom_components.intelbras_isic.bridge.LoopbackProxy", return_value=proxy
        ),
    ):
        assert await manager.async_start() == 45000
        assert await manager.async_start() == 45000
        assert manager.ready
        assert manager.successful_starts == 1
        transport.connect.assert_called_once()
        transport.alive = False
        assert not manager.ready
        transport.connect.side_effect = lambda: setattr(transport, "alive", True)
        assert await manager.async_start() == 45000
        assert manager.successful_starts == 2
        await manager.async_stop()
        assert not manager.ready
        assert manager.local_port is None
        assert manager.uptime_seconds is None
        assert transport.close.call_count == 2
        assert proxy.close.call_count == 2


async def test_failed_start_closes_transport_and_redacts_details():
    transport = MagicMock()
    transport.connect.side_effect = OSError("private serial and password")
    manager = BridgeManager(
        "synthetic-device",
        554,
        application_key="synthetic-key",
        p2p_password="synthetic-password",
    )
    with (
        patch(
            "custom_components.intelbras_isic.bridge.Transport", return_value=transport
        ),
        pytest.raises(BridgeError, match="Unable to establish") as raised,
    ):
        await manager.async_start()
    transport.close.assert_called_once()
    assert not manager.ready
    assert "private" not in manager.last_error
    assert manager.successful_starts == 0
    assert raised.value.__cause__ is None
    assert raised.value.__suppress_context__


async def test_cancelled_start_joins_thread_and_closes_transport():
    began = threading.Event()
    closed = threading.Event()

    def connect():
        began.set()
        assert closed.wait(timeout=3)
        raise OSError("Socket closed during cancellation")

    transport = MagicMock()
    transport.connect.side_effect = connect
    transport.close.side_effect = closed.set
    manager = BridgeManager(
        "synthetic-device",
        554,
        application_key="synthetic-key",
        p2p_password="synthetic-password",
    )
    with patch(
        "custom_components.intelbras_isic.bridge.Transport", return_value=transport
    ):
        task = asyncio.create_task(manager.async_start())
        assert await asyncio.to_thread(began.wait, 2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert closed.is_set()
    assert not manager.ready
    assert manager._transport is None
