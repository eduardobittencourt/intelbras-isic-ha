"""Registration can use healthy endpoints anywhere in the discovery list."""

import struct
from collections import deque
from unittest.mock import Mock

import pytest

from custom_components.intelbras_isic.transport import client as module
from custom_components.intelbras_isic.transport.client import (
    Configuration,
    Transport,
    TransportError,
)
from custom_components.intelbras_isic.transport.discovery import ProtocolError, Server


def heartbeat():
    return (
        struct.pack("<HH", 0x2012, 1001)
        + b"192.0.2.99".ljust(16, b"\0")
        + struct.pack("<HHII", 5000, 0, 0, 0)
    )


@pytest.fixture
def registration(monkeypatch):
    transport = Transport(Configuration("cloud.example", 1250, "key", "pass", "serial"))
    clock = [0.0]
    packets = deque()
    responding = {}
    sent = []
    sock = Mock()

    def send(payload, endpoint):
        sent.append(endpoint)
        if endpoint in responding:
            packets.append((responding[endpoint], endpoint))

    def select(read, write, error, timeout):
        if packets:
            return [sock], [], []
        clock[0] += timeout
        return [], [], []

    sock.sendto.side_effect = send
    sock.recvfrom.side_effect = lambda size: packets.popleft()
    transport._main = sock
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(module.select, "select", select)
    monkeypatch.setattr(module, "registration_response", lambda packet, key: 25)
    transport._exchange = Mock(return_value=b"registered")
    return transport, responding, sent, packets, clock


def servers(count):
    return tuple(Server(f"192.0.2.{index + 1}", 1250) for index in range(count))


def test_healthy_server_after_first_seven_unavailable_endpoints(registration):
    transport, responding, sent, _, _ = registration
    candidates = servers(27)
    endpoint = (candidates[7].address, 1250)
    responding[endpoint] = heartbeat()
    transport._register(candidates)
    assert transport._server == endpoint
    assert transport._interval == 25
    assert transport.metrics["verified_registrations"] == 1
    assert len(sent) == 27
    assert transport._exchange.call_args.args[1] == endpoint


def test_heartbeat_loss_is_retried_without_duplicate_endpoints(registration):
    transport, responding, sent, _, _ = registration
    candidates = servers(1)
    endpoint = (candidates[0].address, 1250)
    original_send = transport._main.sendto.side_effect

    def send(payload, address):
        if sent:
            responding[endpoint] = heartbeat()
        original_send(payload, address)

    transport._main.sendto.side_effect = send
    transport._register(candidates + candidates)
    assert sent == [endpoint, endpoint]
    assert transport._server == endpoint


def test_all_unavailable_servers_have_bounded_retries(registration):
    transport, _, sent, _, clock = registration
    with pytest.raises(TransportError, match="No server accepted"):
        transport._register(servers(27))
    assert len(sent) == 81
    assert clock[0] == pytest.approx(3)
    transport._exchange.assert_not_called()


def test_unknown_sender_and_malformed_heartbeats_are_ignored(registration):
    transport, responding, _, packets, _ = registration
    candidates = servers(2)
    packets.append((heartbeat(), ("198.51.100.1", 1250)))
    responding[(candidates[0].address, 1250)] = b"malformed"
    responding[(candidates[1].address, 1250)] = heartbeat()
    transport._register(candidates)
    assert transport._server == (candidates[1].address, 1250)
    assert transport._exchange.call_count == 1


@pytest.mark.parametrize(
    "error", [TransportError("timeout"), ProtocolError("rejected")]
)
def test_registration_failure_tries_another_responsive_server(registration, error):
    transport, responding, _, _, _ = registration
    candidates = servers(2)
    for server in candidates:
        responding[(server.address, server.port)] = heartbeat()
    transport._exchange.side_effect = [error, b"registered"]
    transport._register(candidates)
    assert transport._server == (candidates[1].address, 1250)
    assert transport.metrics["registration_attempts"] == 2


def test_registration_exchange_uses_remaining_deadline(registration):
    transport, responding, _, _, clock = registration
    responding[("192.0.2.1", 1250)] = heartbeat()

    def timeout(*args):
        clock[0] += args[-1]
        raise TransportError("timeout")

    transport._exchange.side_effect = timeout
    with pytest.raises(TransportError, match="No server accepted"):
        transport._register(servers(1), timeout=0.5)
    assert transport._exchange.call_args.args[-1] == 0.5
    assert clock[0] == 0.5


def test_cancelled_registration_sends_nothing(registration):
    transport, _, sent, _, _ = registration
    transport._stop.set()
    with pytest.raises(TransportError, match="Connection cancelled"):
        transport._register(servers(27))
    assert sent == []


def test_registration_can_be_cancelled_while_waiting(registration):
    transport, _, _, _, _ = registration
    transport._main.sendto.side_effect = lambda *args: transport._stop.set()
    with pytest.raises(TransportError, match="Connection cancelled"):
        transport._register(servers(1))
    transport._exchange.assert_not_called()
