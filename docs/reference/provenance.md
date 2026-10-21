# Transport provenance

## Implementation and research method

The transport was written from scratch in Python to replace a proprietary ARM
library used by an earlier private Home Assistant integration. The public
package contains no vendor source code, redistributed vendor binary,
`ctypes`/`dlopen` mechanism, QEMU invocation, or SDK dependency.

Research included reading the existing wrapper, inspecting symbols and
instructions in the private reference ELF binary, and testing interoperability
with the project owner's recorder. This was **not clean-room development**.
Writing new code and separating it from the SDK does not by itself resolve
the contractual and intellectual-property analysis associated with publication.
The project has not obtained a documented resolution or vendor permission
covering those questions.

The separate [APK extraction guide](../guides/credentials.md) documents static
analysis of iSIC Lite 2.8.6 to locate application parameters. It publishes
localizers and argument roles, without redistributing their values or vendor
code. In an October 2026 support conversation reported by the maintainer,
Intelbras said recorder Cloud/P2P communication is homologated only for its own
software and applications. That contact did not provide a credential provisioning
route for this client.

## Cryptographic compatibility

TEA was implemented from the mathematical definition of the standard algorithm,
with a known-vector test. Its use reproduces a legacy format. In discovery and
registration, the TEA key is the transmitted header, so this encryption does not
provide confidentiality against someone observing the traffic. MD5 is used for
P2P password compatibility. See [Protocol](protocol.md) for the transport's
security properties.

## Published artifacts

Distributed tests use fictitious identities, `*.example`, and documentation
addresses in `192.0.2.0/24`. They do not include real credentials, serial numbers,
the owner's public addresses, camera images, or bytes captured from the camera.

Research disassemblies, captures, the proprietary library, and earlier private
history are not part of the public repository. Public history begins with the
Python source and synthetic test parameters. Dated functional evidence is
collected in [Validation](../development/validation.md).

## Licensing boundaries

The MIT License covers the project's original code. It does not grant rights
to vendor credentials, SDKs, firmware, trademarks, or access to the Cloud service.
The integration receives service parameters through the user's private HA
configuration.

The official iSIC Lite icon is vendor artwork and is excluded from the MIT
License. Its source and separate rights are documented in
[Third-party notices](../../THIRD_PARTY_NOTICES.md).
