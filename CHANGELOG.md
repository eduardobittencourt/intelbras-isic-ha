# Changelog

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
