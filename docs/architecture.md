# Architecture

The integration has three layers:

1. Home Assistant entities and config flow.
2. An asynchronous lifecycle manager that owns one Python transport per entry.
3. A Python UDP P2P client that discovers servers, registers a client, negotiates
   a direct IPv4 connection and carries reliable multiplexed TCP streams.

The TCP proxy explicitly binds `127.0.0.1` on an ephemeral port. UDP sockets
handle cloud and peer traffic. Home Assistant and FFmpeg authenticate directly
to the remote recorder through the tunnel, using RTSP-over-TCP. The transport does not launch subprocesses or load vendor libraries.

## Runtime lifecycle

- Config flow starts a temporary tunnel and performs an authenticated RTSP
  `DESCRIBE` before accepting the entry.
- Entry setup starts a persistent tunnel and repeats the probe.
- Camera entities ask the bridge manager for the current local port.
- Entry unload closes the proxy, sockets and workers outside the HA event loop.
- Failed and cancelled startup closes and joins the worker being established.
- A stopped peer worker is recreated when a camera source is requested.

## Packaging boundary

The independently written transport lives in the local
`intelbras-isic-transport` package and is vendored into `transport/` while it has
no published version. It uses Python's standard library only. Its standalone
tests cover packet loss, reordering, malformed messages and buffer bounds;
the integration tests cover the asynchronous adapter lifecycle.

See [Transport provenance](transport-provenance.md) for the research method.
The public repository begins with source-only history. The implementation uses
vendor Cloud endpoints and application credentials supplied in the private HA
config entry; it does not contain those credentials. Existing version-1 entries
migrate to version 2 and request reauthentication if the Cloud fields are missing.
