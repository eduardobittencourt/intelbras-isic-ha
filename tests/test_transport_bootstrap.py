"""DNS failover prevents one unavailable bootstrap host from blocking setup."""

import socket
import struct
from unittest.mock import patch

import pytest

from custom_components.intelbras_isic.transport import tea
from custom_components.intelbras_isic.transport.client import (
    Configuration,
    Transport,
    TransportError,
)


def _address(value):
    return (socket.AF_INET, socket.SOCK_DGRAM, 17, "", (value, 1250))


def _reply():
    prefix = struct.pack("<HHIHHI", 0x2012, 5002, 123, 1, 1, 42)
    payload = tea.encrypt(b"192.0.2.50:1250|cloud.example|ipv6.example\n\0", prefix)
    return prefix + struct.pack("<I", len(payload)) + payload


@pytest.mark.parametrize("first_result", [TransportError("timeout"), b"malformed"])
def test_unavailable_or_invalid_bootstrap_falls_back_to_next_dns_address(first_result):
    transport = Transport(Configuration("cloud.example", 1250, "key", "pass", "serial"))
    with (
        patch(
            "socket.getaddrinfo",
            return_value=[
                _address("192.0.2.10"),
                _address("192.0.2.10"),
                _address("192.0.2.11"),
            ],
        ),
        patch.object(
            transport, "_exchange", side_effect=[first_result, _reply()]
        ) as query,
    ):
        servers = transport._discover()
    assert servers[0].address == "192.0.2.50"
    assert [call.args[1] for call in query.call_args_list] == [
        ("192.0.2.10", 1250),
        ("192.0.2.11", 1250),
    ]
    assert transport.metrics["bootstrap_endpoints"] == 2
    assert transport.metrics["bootstrap_attempts"] == 2


def test_all_unavailable_bootstrap_addresses_have_a_bounded_attempt_count():
    transport = Transport(Configuration("cloud.example", 1250, "key", "pass", "serial"))
    with (
        patch(
            "socket.getaddrinfo",
            return_value=[_address(f"192.0.2.{n}") for n in range(1, 20)],
        ),
        patch.object(
            transport, "_exchange", side_effect=TransportError("timeout")
        ) as query,
        pytest.raises(TransportError, match="No Cloud discovery endpoint responded"),
    ):
        transport._discover()
    assert query.call_count == 8
    assert all(call.args[-1] == 2 for call in query.call_args_list)


def test_cancelled_bootstrap_does_not_send_discovery_requests():
    transport = Transport(Configuration("cloud.example", 1250, "key", "pass", "serial"))
    transport.close()
    with (
        patch("socket.getaddrinfo", return_value=[_address("192.0.2.10")]),
        patch.object(transport, "_exchange") as query,
        pytest.raises(TransportError, match="Connection cancelled"),
    ):
        transport._discover()
    query.assert_not_called()
