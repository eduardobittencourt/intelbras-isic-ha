import queue
import socket
import struct
import threading
import time

import pytest

from custom_components.intelbras_isic.transport.client import (
    Configuration,
    LoopbackProxy,
    Transport,
)
from custom_components.intelbras_isic.transport.wire import (
    VDT_PREFIX,
    FrameDecoder,
    application_frame,
    vdt_ack,
    vdt_data,
)

pytestmark = [
    pytest.mark.usefixtures("socket_enabled"),
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_proxy_stream_retransmits_a_lost_packet_and_preserves_order():
    """Exercise the real worker with a localhost UDP peer that drops packet one."""
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("127.0.0.1", 0))
    server.settimeout(2)
    transport = Transport(Configuration("unused.example", 1250, "test", "test", "test"))
    transport._socket = Transport._socket_new()
    transport._main = Transport._socket_new()
    transport._peer = server.getsockname()
    transport._server = server.getsockname()
    transport._interval = 25
    transport._last_peer = time.monotonic()
    transport._last_hello = time.monotonic()
    transport._last_registration = time.monotonic()
    transport._peer_window = 16
    results = []

    def peer():
        dropped = False
        packets = {}
        decoder = FrameDecoder()
        next_sequence = 1
        while not transport._stop.is_set():
            packet, address = server.recvfrom(65535)
            if packet[:4] != VDT_PREFIX + b"\x02":
                continue
            sequence = struct.unpack_from("!I", packet, 4)[0]
            if sequence == 1 and not dropped:
                dropped = True
                continue
            packets[sequence] = packet[16:]
            while next_sequence in packets:
                results.extend(decoder.feed(packets.pop(next_sequence)))
                next_sequence += 1
            highest = max(packets, default=next_sequence - 1)
            missing = tuple(
                i for i in range(next_sequence, highest) if i not in packets
            )
            server.sendto(vdt_ack(highest, missing), address)
            if any(kind == 0 for _, kind, _ in results):
                reply = application_frame(1, 0, b"RTSP/1.0 200 OK\r\n")
                # Deliver the reply tail first to exercise the receiving worker.
                server.sendto(vdt_data(2, reply[12:]), address)
                server.sendto(vdt_data(1, reply[:12]), address)
                return

    mock = threading.Thread(target=peer, daemon=True)
    transport._worker = threading.Thread(target=transport._run, daemon=True)
    mock.start()
    transport._worker.start()
    try:
        stream = transport.open_stream()
        stream.send(b"OPTIONS / RTSP/1.0\r\n")
        assert stream.receive(timeout=3) == b"RTSP/1.0 200 OK\r\n"
        assert results[-1] == (1, 0, b"OPTIONS / RTSP/1.0\r\n")
        assert transport.metrics["retransmissions"] >= 1
        assert transport.failure is None
    finally:
        transport.close()
        mock.join(timeout=2)
        server.close()
    assert not transport.alive
    assert transport._socket.fileno() == -1
    assert transport._main.fileno() == -1


def test_proxy_keeps_downstream_media_alive_when_client_sends_no_more_commands():
    """Real loopback TCP remains open beyond the upstream polling timeout."""

    class MediaStream:
        def __init__(self):
            self.media = queue.Queue()
            self.sent = threading.Event()

        def send(self, payload):
            assert payload == b"PLAY / RTSP/1.0\r\n"
            self.sent.set()

        def receive(self, timeout):
            return self.media.get(timeout=timeout)

        def close(self):
            self.media.put(b"")

    class Session:
        alive = True

        def __init__(self):
            self.stream = MediaStream()

        def open_stream(self):
            return self.stream

    session = Session()
    with (
        LoopbackProxy(session) as proxy,
        socket.create_connection(("127.0.0.1", proxy.port)) as client,
    ):
        assert proxy._listener.getsockname()[0] == "127.0.0.1"
        client.settimeout(3)
        client.sendall(b"PLAY / RTSP/1.0\r\n")
        assert session.stream.sent.wait(1)
        # An RTSP viewer can be silent upstream throughout media playback.
        time.sleep(1.2)
        session.stream.media.put(b"interleaved-media")
        assert client.recv(100) == b"interleaved-media"
