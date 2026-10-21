# Changelog

## [0.3.4] - 2026-10-21

- Consolidate documentation into English user guides, technical reference, and
  development evidence, with a single documentation index.
- Document verified static extraction of Cloud application parameters from
  iSIC Lite 2.8.6 without distributing the values.
- Remove Portuguese documentation and interface translations. Default camera
  names now use "Channel"; camera unique identifiers remain unchanged.

## [0.3.3] - 2026-10-14

- Refresh CI actions, PyAV, PyTurboJPEG and Ruff, including Python 3.14 formatting.
- Test the minimum Home Assistant 2026.9.4 and stable 2026.10.1 with their matching
  test harnesses. Let the harness supply its required NumPy version instead of
  maintaining a conflicting direct pin.
- Document the remaining reliability work: automatic session recovery, channel
  isolation, transport diagnostics, sustained-operation tests and protocol coverage.

## [0.3.2] - 2026-10-09

- Use the official Intelbras iSIC Lite app icon in Home Assistant and the README.
- Remove the generic camera/cloud artwork and document the vendor artwork source
  and separate rights in the third-party notices.

## [0.3.1] - 2026-10-05

- Try alternate IPv4 DNS addresses for Cloud discovery when the first endpoint
  times out or returns an invalid response. Limit retries and honor cancellation.
- Add regression tests for bootstrap failover and document the HACS installation
  and migration validation on the owner's Home Assistant instance.

## [0.3.0] - 2026-10-05

First public, source-only release.

- Replace the proprietary ARM runtime with an independently written Python
  transport for direct IPv4 P2P and multiplexed RTSP-over-TCP.
- Remove vendor binaries, QEMU, ARM rootfs, bundled Cloud credentials and vendor artwork.
- Supply Cloud application credentials through private Home Assistant configuration.
- Preserve existing entry/entity identifiers and support reauthentication and reconfiguration.
- Redact Cloud credentials in diagnostics and suppress sensitive transport error details.
- Include transport reliability tests, HACS metadata, public CI and bilingual installation guides.
- Provide an original MIT-licensed community icon.

Relay, IPv6 negotiation and automatic recovery of active video sessions remain
out of scope for this release. New installations require separately supplied
Cloud application credentials.
