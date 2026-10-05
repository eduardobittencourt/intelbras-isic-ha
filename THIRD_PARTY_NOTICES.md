# Third-party notices

The MIT License covers the original integration code, independently written
Python transport and community icon (`assets/icon.svg` and its PNG rendering).
No Intelbras logo, proprietary DLL/SDK, QEMU executable or ARM root filesystem
is included in this public repository or its public Git history.

The private predecessor is retained separately and is not part of this release.
Protocol research included inspection of that reference binary and tests with
the project owner's recorder; this was not clean-room development. See
[Transport provenance](docs/transport-provenance.md).

The implementation uses the standard TEA algorithm and MD5 to interoperate with
a legacy wire format. The transport uses the Python standard library; Home
Assistant and its FFmpeg/stream dependencies are provided by the user's HA
installation and are subject to their respective licenses.

Cloud application credentials are supplied by the user and are not distributed.
The MIT License does not grant rights to vendor credentials, services, firmware,
SDKs or trademarks. Intelbras and iSIC are trademarks of Intelbras S.A.; this
community project is not affiliated with or endorsed by Intelbras.
