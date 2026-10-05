# Security policy

## Supported versions

The latest public release is supported. Protocol compatibility remains experimental.

## Reporting a vulnerability

Do not open a public issue containing a vulnerability, credential, serial
number, camera image, or cloud protocol secret. Use GitHub's private security
advisory feature for this repository.

Include the affected version, impact, reproduction steps with sanitized data,
and any suggested mitigation. Reports will be acknowledged as soon as
practical, but this experimental project has no guaranteed response SLA.

## Sensitive information

- Never attach `.storage/core.config_entries`.
- Redact serial numbers, usernames, passwords, RTSP URLs, tokens, and images.
- Never post Cloud application credentials in public issues, code or logs.
- Home Assistant config entries contain sensitive data; diagnostics redaction
  does not encrypt those entries. Protect your HA instance and backups.
- Diagnostics are designed to redact config-entry secrets, but reporters must
  still review files before sharing them.
