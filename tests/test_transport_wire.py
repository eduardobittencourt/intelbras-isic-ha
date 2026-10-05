import struct

import pytest

from custom_components.intelbras_isic.transport.client import Configuration
from custom_components.intelbras_isic.transport.discovery import ProtocolError
from custom_components.intelbras_isic.transport.wire import (
    MAX_FRAME,
    WINDOW,
    FrameDecoder,
    ReceiveWindow,
    application_frame,
    peer_endpoints,
    vdt_data,
)


def test_reordering_missing_packets_and_duplicates():
    receiver = ReceiveWindow()
    ordered, ack = receiver.accept(vdt_data(3, b"third"))
    assert ordered == b""
    assert struct.unpack_from("!HHI", ack, 4) == (WINDOW - 1, 2, 3)
    assert struct.unpack_from("!2I", ack, 16) == (1, 2)
    assert receiver.accept(vdt_data(1, b"first"))[0] == b"first"
    assert receiver.accept(vdt_data(1, b"first"))[0] == b""
    assert receiver.accept(vdt_data(2, b"second"))[0] == b"secondthird"
    assert receiver.accept(vdt_data(3, b"third"))[0] == b""
    assert not receiver.pending


def test_receive_window_rejects_unbounded_and_truncated_datagrams():
    receiver = ReceiveWindow()
    with pytest.raises(ProtocolError):
        receiver.accept(vdt_data(WINDOW + 1, b"outside"))
    with pytest.raises(ProtocolError):
        receiver.accept(vdt_data(1, b"truncated")[:-1])
    assert receiver.next_sequence == 1
    assert receiver.pending == {}


def test_frame_decoder_handles_fragmentation_and_coalescing():
    decoder = FrameDecoder()
    wire = application_frame(1, 0, b"RTSP/1.0 200 OK\r\n") + application_frame(
        2, 0, b"other channel"
    )
    assert decoder.feed(wire[:5]) == []
    assert decoder.feed(wire[5:13]) == []
    assert decoder.feed(wire[13:]) == [
        (1, 0, b"RTSP/1.0 200 OK\r\n"),
        (2, 0, b"other channel"),
    ]
    assert not decoder.buffer


def test_frame_decoder_rejects_oversized_length_before_allocating_payload():
    with pytest.raises(ProtocolError):
        FrameDecoder().feed(struct.pack("<HHI", 1, 0, MAX_FRAME + 1))


def test_connection_offer_cannot_select_another_device_or_client():
    packet = bytearray(588)
    struct.pack_into("<HHI", packet, 0, 0x2012, 1004, 22)
    packet[8:108] = b"test-device".ljust(100, b"\0")
    packet[108:208] = b"test-client".ljust(100, b"\0")
    packet[208:224] = b"192.0.2.7".ljust(16, b"\0")
    struct.pack_into("<H", packet, 224, 45000)
    assert peer_endpoints(packet, "test-client", "test-device") == (
        ("192.0.2.7", 45000),
    )
    for identity, serial in (
        ("other-client", "test-device"),
        ("test-client", "other-device"),
    ):
        with pytest.raises(ProtocolError):
            peer_endpoints(packet, identity, serial)


def test_configuration_repr_excludes_credentials_and_device_identity():
    config = Configuration(
        "cloud.example", 1250, "key-private", "password-private", "serial-private"
    )
    assert "private" not in repr(config)
