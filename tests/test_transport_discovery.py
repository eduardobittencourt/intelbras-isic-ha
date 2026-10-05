import struct

import pytest

from custom_components.intelbras_isic.transport import tea
from custom_components.intelbras_isic.transport.discovery import (
    ProtocolError,
    discovery_response,
    heartbeat_response,
    registration_response,
)


def test_discovery_parses_encrypted_server_list():
    prefix = struct.pack("<HHIHHI", 0x2012, 5002, 123, 1, 2, 42)
    ciphertext = tea.encrypt(
        b"192.0.2.10:1250|cloud.example|ipv6.example\n192.0.2.11:1251||\n\0", prefix
    )
    servers = discovery_response(
        prefix + struct.pack("<I", len(ciphertext)) + ciphertext
    )
    assert [(s.address, s.port) for s in servers] == [
        ("192.0.2.10", 1250),
        ("192.0.2.11", 1251),
    ]
    assert servers[0].ipv6_hostname == "ipv6.example"


@pytest.mark.parametrize(
    "packet",
    [
        b"",
        b"\x12\x20\x8a\x13",
        struct.pack("<HHIHHII", 0x2012, 5002, 1, 1, 2, 42, 100),
        bytes(24),
    ],
)
def test_discovery_rejects_truncated_or_unexpected_messages(packet):
    with pytest.raises(ProtocolError):
        discovery_response(packet)


def test_heartbeat_keeps_observed_address_out_of_repr():
    packet = (
        struct.pack("<HH", 0x2012, 1001)
        + b"192.0.2.9\0".ljust(16, b"\0")
        + struct.pack("<HHII", 45000, 0, 123, 456)
    )
    observation = heartbeat_response(packet)
    assert (
        observation.port,
        observation.echoed_seconds,
        observation.echoed_microseconds,
    ) == (
        45000,
        123,
        456,
    )
    assert "192.0.2.9" not in repr(observation)


def _registration(accepted=1, timestamp=100, key="synthetic-test-key"):
    prefix = struct.pack("<HHIII", 0x2012, 1013, accepted, 25, timestamp)
    return (
        prefix
        + tea.encrypt(key.encode().ljust(32, b"\0"), prefix)
        + struct.pack("<I", 5)
    )


def test_registration_checks_acceptance_time_and_returned_key():
    assert registration_response(_registration(), "synthetic-test-key", now=100) == 25
    for packet, key in (
        (_registration(accepted=0), "synthetic-test-key"),
        (_registration(timestamp=70), "synthetic-test-key"),
        (_registration(), "wrong-key"),
    ):
        with pytest.raises(ProtocolError):
            registration_response(packet, key, now=100)
