# Reliability roadmap

This is an assessment of the implementation on 2026-10-14, not a list of
features delivered by the maintenance release. Python is suitable for this
transport; reliability depends on lifecycle, failure isolation, protocol
coverage and evidence under sustained load.

## Existing foundation

The Home Assistant entities, asynchronous bridge manager and standard-library
transport already form separate layers. Startup is serialized, cancellation
cleans up the worker, queues and packet windows have bounds, and the proxy binds
only to loopback. Tests cover discovery failover, retransmission, reordering,
duplicate packets, malformed messages and lifecycle cleanup.

At the time of the assessment, the 44-test suite reported 65% branch-inclusive
coverage. The network client was at 57%, the RTSP probe at 17% and the camera
platform at 51%. These figures identify unexercised paths; they do not measure
field reliability.

## 1. Recover an existing session automatically

`BridgeManager.async_start()` recreates a failed transport when a camera asks
for a source. There is no background reconnect supervisor, and recreation can
change the local port. An existing HA stream may retain its previous URL.

Add explicit connection states, bounded retries with backoff and jitter, and a
single owner for reconnects and cancellation. Keep a stable local endpoint or
explicitly coordinate source replacement with HA's stream lifecycle. Push
availability updates to entities when connection state changes.

Acceptance: simulated peer loss, restored connectivity and DNS changes recover
both snapshots and an already-running HA stream without reloading the entry.
Unloading during retries must leave no sockets, workers or retry tasks behind.

## 2. Isolate slow and failed channels

All channels share one transport. A full incoming queue currently raises
`TransportError` from the peer worker, ending the whole session. The eight-stream
limit is shared by snapshots and live sessions, with no admission queue or
reserved capacity for setup probes.

Define per-stream overload behavior, close only the affected channel when the
protocol permits it, and provide bounded admission and clear capacity errors.
Coordinate snapshots with live sessions so a temporary still request cannot
silently destabilize unrelated video.

Acceptance: eight consumers, a stalled consumer, rapid open/close cycles and a
ninth request produce bounded memory use and predictable errors. Healthy
channels continue when another consumer fails.

## 3. Make failures diagnosable and testable

The transport already counts bytes and retransmissions, but HA diagnostics only
expose bridge readiness, starts, uptime and a generic startup error. Export
sanitized counters and structured failure stages, including reconnect count,
active streams, queue pressure and time since the last valid peer response.
Preserve redaction and avoid credentials, serials and camera frames.

Build an in-process Cloud/peer/RTSP simulator. Exercise loss, jitter, duplicates,
reordering, malformed or oversized messages, zero receive windows, registration
expiry and concurrent shutdown. Expand real RTSP authentication and camera
tests, including timeout and error paths. Evaluate adaptive retransmission
timing using measurements rather than changing the wire protocol speculatively.

Acceptance: each recovery and resource-bound scenario has a deterministic test;
diagnostics distinguish failure stages without exposing private values.

## 4. Establish sustained-operation and compatibility gates

Short successful media checks do not establish continuous multi-day playback.
Run explicit 24–72 hour tests with all channels, recording only aggregate CPU,
memory, descriptor/thread counts, retries, reconnects and decoded-frame counts.
Test controlled disconnects against a disposable simulator before scheduling
real-network interruptions in the homelab.

Keep CI on the minimum supported HA and a current stable HA, with compatible
test harnesses. Test aarch64 as well as x86_64, multiple recorder/firmware
combinations and constrained networks before claiming wider compatibility.

Acceptance: no growing resource trend, no unexplained stalled channels, and
documented recovery times and tested equipment. CI and a real HACS installation
must agree on the release being validated.

## 5. Expand access and protocol coverage

New users still need separately supplied Cloud application parameters. The
[credential guide](../guides/credentials.md) now documents static extraction for
iSIC Lite 2.8.6. That does not provide account-based provisioning or remove the
service and permission dependencies described in
[Provenance](../reference/provenance.md).
Cloud relay, IPv6 and legacy peers without VDT remain unimplemented; direct
IPv4 success does not establish support for those paths.

Treat each protocol addition as separate research with sanitized fixtures and
real-device validation. Publishing the transport as its own versioned library
can help independent consumers later; package extraction alone does not solve
session recovery or protocol coverage.

The implementation order should favor session recovery, isolation and
diagnostics before expanding the supported network/protocol surface.

Historical transport and installation checks are consolidated in the
[validation record](validation.md); they do not establish the acceptance criteria
above as completed.
