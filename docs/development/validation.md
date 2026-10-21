# Validation record

This document consolidates dated observations from transport development,
release installation, and APK analysis. Results apply to the tested equipment,
network, and versions. Reorganizing this documentation did not repeat these
checks or establish compatibility with other recorders.

All real-device checks used the owner's remote eight-channel recorder. Its
exact hardware model and firmware were not recorded in these reports. Images,
video segments, credentials, and serial numbers are not published as evidence.

## Initial Python transport: October 5, 2026

The Python transport and asynchronous adapter were tested in the development
environment against the recorder already configured in the owner's HA instance.
This initial development branch was not installed into HA during those checks.

| Check | Observation |
| --- | --- |
| Cloud bootstrap | 27 servers discovered; application registration validated |
| Recorder connection | Direct IPv4 P2P negotiated; authenticated RTSP through the Python tunnel |
| First decoded frame | H.264, 704×480, after 5.36 seconds |
| Eight channels | One authenticated frame per channel after 5.23–5.37 seconds |
| Eight-channel decoding | 239 frames per channel, 1,912 total; 30 seconds of decoding per video, approximately 35.7 seconds elapsed |
| Registration renewal | Validated during the eight-channel run without transport failure |
| Single-channel run | 273 frames over 35 seconds of decoding, 40.25 seconds elapsed, without transport failure |
| Existing HA reference integration | 243 frames in 35.12 seconds elapsed |
| Real asynchronous adapter | Authenticated `DESCRIBE` on all eight channels, decoded 704×480 H.264, and confirmed session shutdown |
| Automated checks at that stage | 19 transport tests and 11 integration tests passed; Ruff and formatting passed in both development projects |

Synthetic tests exercised loss/retransmission, reordering, duplication, buffer
bounds, malformed messages, and an RTSP client that stops sending commands while
continuing to receive media. Adapter tests covered idempotent startup, dead-worker
replacement, error cleanup, and cancellation during connection.

A sustained-playback failure was corrected: the proxy must not close TCP merely
because the client stops sending commands while playing media. The regression
test keeps receiving media after the outgoing polling timeout.

Device credentials and serial were read from existing private configuration
and used in memory. Research captures and disassemblies stayed outside the
public branch. Before publication, application parameters were removed from
source and moved to private HA configuration; vendor binaries and earlier
history were kept separately. The first public release used original artwork,
which was later replaced in v0.3.2.

## HACS installation: v0.3.1, October 5, 2026

The public release was installed on HA 2026.9.4 with HACS 2.0.5 as a custom
repository, using HACS's WebSocket installer. No manual copy of the new code
was used. The recorder remained on another network, reached through Intelbras
Cloud and P2P.

- All 22 installed integration files matched release SHA-256 hashes.
- HACS retained eight old binaries under the previous `bridge/` directory.
  That obsolete directory was removed after backing up the HA installation.
- Configuration checking passed and HA Core restarted successfully.
- The config entry migrated from version 1 to version 2. Reauthentication
  supplied the Cloud parameters, stored only in private HA configuration.
- Existing entry, device, and camera identifiers were preserved.

| Check | Result |
| --- | --- |
| Existing cameras | All 8 available |
| Enabled entities, including diagnostics | All 13 available |
| Snapshots through HA camera API | 8 valid JPEGs at 704×480 |
| HLS video through HA API | All 8 H.264 channels decoded at 704×480 |
| Integration diagnostics | Serial, device password, application key, and P2P password redacted |
| Tunnel after media checks | Ready, without session recreation |
| Official config-entry reload | Loaded, 8 cameras available, and a valid new snapshot |
| Native binaries in the final installed integration | 0 |

Streams were requested through `camera/stream`, playlists were read, and frames
were decoded from HA-generated HLS segments. Segments were processed in memory.
This exercised HA → Python transport → remote recorder → HLS.

### Discovery failover correction

Initial v0.3.0 snapshot and video checks passed, but a later reload entered
`setup_retry`. Discovery DNS returned six IPv4 addresses: the first selected by
HA did not respond; the other five did. The client originally tried only the
first address.

v0.3.1 added bounded attempts across distinct addresses. After installing it
through HACS and restarting Core, all eight snapshot and video checks passed
again. Official config-entry reload also passed, making all 13 entities
available and returning a valid new snapshot in approximately six seconds.

### Release checks

All 44 automated tests passed, covering migration, reauthentication,
reconfiguration, cancellation, packet loss/reordering, redaction, and discovery
fallback after timeout or an invalid response. Ruff, formatting, Tests,
Hassfest, and HACS validation passed for the release code.

Public files and historical blobs were checked for the real credentials and
serials examined during that validation, and for ELF binaries, with no matches
reported. Earlier history was kept in a separate private repository; the
proprietary library blob was not anonymously accessible through the public repo.
These checks are dated evidence, not a substitute for reviewing new changes.

## Icon update: v0.3.2, October 9, 2026

v0.3.2 replaced the original generic artwork with the official iSIC Lite icon.
See [Third-party notices](../../THIRD_PARTY_NOTICES.md) for its source and rights.

- Installed through the HACS WebSocket installer on HA 2026.10.0.
- All 23 installed files matched release SHA-256 hashes, with no missing,
  extra, or modified files after excluding `__pycache__`.
- Configuration checking and Core restart passed. The existing entry returned
  to `loaded`; all 8 cameras and 13 enabled entities kept their identifiers.
- Eight valid JPEG snapshots were obtained after restart. HACS reported v0.3.2
  installed, without a pending update.
- All eight icon/logo variants, including dark theme and `@2x`, returned HTTP
  200 and `image/png` through `/api/brands/integration/intelbras_isic/`.
  Each returned the same official icon bytes and SHA-256.
- All 44 tests, Ruff, formatting, Tests, Hassfest, and HACS checks passed.

The included image was inspected visually and all frontend asset endpoints
were checked. A rendered browser page was not inspected. Snapshots were
processed in memory. HLS playback was not repeated because transport behavior
was unchanged by the icon update.

## Maintenance: v0.3.3, October 14, 2026

This release updated development/CI dependencies and Python 3.14 formatting,
and added a compatibility matrix. It did not implement the reconnection
supervisor, Cloud relay, or IPv6 described in the [roadmap](roadmap.md).

- All 44 tests passed on minimum HA 2026.9.4 and stable HA 2026.10.1, using
  harnesses 0.13.367 and 0.13.372 respectively. Dependency consistency, Ruff,
  formatting, Hassfest, and HACS checks passed locally or in the relevant CI jobs.
- The harness selected NumPy 2.3.2. A standalone update to 2.5.3 was incompatible;
  the redundant direct pin was removed.
- The previous integration was backed up, then v0.3.3 was downloaded through the
  HACS WebSocket installer on HA 2026.10.1. All 23 files matched release hashes,
  excluding `__pycache__`.
- `ha core check` passed and Core restarted. The entry was `loaded`, with all
  8 cameras and 13 enabled entities available under the same identifiers.
- Eight JPEG snapshots decoded at 704×480 after restart.
- Eight simultaneous HLS channels ran through the HA API for 301 seconds:
  2,072 H.264 frames per channel at 704×480, 16,576 total, with no playlist,
  download, or decoding errors. The tunnel remained on its first session.
- API diagnostics redacted serial, recorder username/password, application key,
  and P2P password. The tunnel was ready and no bridge error was recorded.
- Official API reload passed, preserving identifiers and entity availability;
  a new snapshot decoded at 704×480.

Runtime media dependencies remained managed by HA: PyAV 19.0.0, NumPy 2.3.2,
PyTurboJPEG 1.8.3, and ha-ffmpeg 3.2.2. The project's PyTurboJPEG update to 2.5.0
applied to its test environment, without manually replacing Core dependencies.
Images and segments were processed in memory.

## APK extraction: October 21, 2026

Static extraction was reproduced with iSIC Lite 2.8.6 (2026041518), JADX 1.5.6,
and Java 21. The base APK and three splits passed signature verification with
apksigner 35.0.2. Both application parameters and their P2P call sites were
located without executing the app or analyzing native libraries. Targeted
class decompilation completed successfully; full-app decompilation had unrelated
partial errors.

The [credential guide](../guides/credentials.md) records hashes, signer
fingerprint, exact localizers, and the reproducible procedure. Values and APKs
are not published. No new recorder session was tested with the extracted values.

## Limits of the evidence

These results do not establish support for all Intelbras hardware or firmware,
Cloud relay, IPv6, other host architectures, or continuous operation for days.
The five-minute v0.3.3 run does not replace a 24–72 hour test and did not exercise
recovery after a network interruption. Current implementation behavior is
separate from the dated observations above; see the [architecture](../reference/architecture.md)
and [reliability roadmap](roadmap.md).
