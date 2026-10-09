# Third-party notices

The MIT License covers the original integration code and independently written
Python transport. The official Intelbras iSIC Lite app icon
(`custom_components/intelbras_isic/brand/icon.png`) is vendor artwork, excluded
from the project's MIT License. Rights to the artwork and trademarks remain
with Intelbras S.A.; its inclusion identifies the product supported by this
community integration and does not imply affiliation or endorsement.

The icon was retrieved on 2026-10-09 from the
[Intelbras S/A app listing on Google Play](https://play.google.com/store/apps/details?id=com.intelbras.isiclite).
The [source PNG](https://play-lh.googleusercontent.com/55dkH_PEXafKaPTxntIvQWqd-bkNMRsKmPhTqUqvbx9MRE8jHhehI4HrG_8Dev8iuV6fG6rBgUVsB6TPntxv=w256-h256)
is 256×256 pixels and is included without modification. Its SHA-256 is
`f1ccaa6daadb63643c0adc7be3f5ba5a896c15c5e37b7a24edf2b693934cb01d`.

No proprietary DLL/SDK, QEMU executable or ARM root filesystem is included in
this public repository or its public Git history.

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
