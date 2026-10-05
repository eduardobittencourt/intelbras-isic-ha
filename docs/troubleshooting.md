# Troubleshooting

## Integration is not listed

Confirm that `custom_components/intelbras_isic/manifest.json` exists under the
Home Assistant config directory, then restart Home Assistant.

## Transport compatibility

The transport uses Python only. Direct IPv4 P2P is supported; devices that need
cloud relay or IPv6 negotiation may time out. ARM hosts no longer require a
QEMU binary, but still need real hardware validation.

## Cannot connect

Check that the device is online in iSIC Lite and that Home Assistant has
outbound internet access. Confirm the supplied Cloud application key/P2P password, serial and remote RTSP port. Port `554`
is the usual default.

## Invalid authentication

The username and password belong to the recorder or camera, not necessarily to
the Intelbras account used by the mobile app.

## Snapshot works but playback does not

Use the H.264 substream. Browser and Home Assistant playback support for H.265
depends on the client. The integration always requests RTSP-over-TCP because
the cloud transport forwards TCP streams rather than separate RTP UDP ports.

## Diagnostics

Open the integration's device page and download diagnostics. Serial number,
username, device password, Cloud application key and P2P password are redacted. Review diagnostics before opening an
issue and remove any additional information you consider sensitive.

## Missing Cloud credentials after upgrading

The public release does not contain the Cloud credentials bundled by the private
preview. Complete the reauthentication prompt with your privately supplied
parameters. Device entries and entity identifiers are preserved. See
[Cloud credentials](cloud-credentials.md).
