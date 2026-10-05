# Cloud credentials and community research

The public integration accepts two application parameters through its config
flow: `cloud_app_key` and `cloud_p2p_password`. It supplies no defaults for them.
They remain in the private HA config entry, are hidden in password fields and
are redacted from integration diagnostics.

| Parameter | Observed role |
| --- | --- |
| `app_key` | Registers the client application with the P2P negotiation service |
| P2P password | Its MD5 is sent in the connection request for the target recorder |
| Device username/password | Authenticates RTSP after the P2P tunnel has opened |
| Conta Intelbras login | Not used by the current implementation |

The exact server-side validation of the P2P password is not established. Two
experiments with an empty wire field did not establish a peer session, whereas
controls with the existing parameter decoded video. This is evidence for the
owner's configuration, not a statement about every firmware.

## Obtaining credentials

There is currently **no supported credential provisioning implemented by this
project**. HACS downloads the integration but does not supply its Cloud
credentials. Use parameters you are authorized to use; do not assume a user's
account access token can replace an application key in the legacy protocol.

Intelbras documents an [API/SDK request channel for DVR/NVR](https://backend.intelbras.com/sites/default/files/2022-08/api-sdk-seguranca-intelbras-whatsapp.pdf).
Whether this channel supplies credentials for the Cloud service and permits use
by an independently implemented open-source client needs confirmation. Receiving
an SDK does not by itself establish permission to redistribute its parameters.

The [iSIC manual](https://guardian.intelbras.com/manual/isic/pt-br/manual.html)
distinguishes account synchronization from P2P connectivity. The official
[GDI platform](https://app-mibo.intelbras.com.br/manual-gdi.html) provides an
account-authorization/token flow for supported Mibo devices, but that is not a
demonstrated replacement for the recorder protocol implemented here.

## Useful contributions

- Document an authorized application-key registration or account provisioning flow.
- Describe credential lifetime, refresh and revocation without exposing values.
- Test interoperability using synthetic fixtures and owned devices.
- Help implement relay, IPv6 and additional recorder variants.

Share endpoint names, sanitized layouts and public documentation. Do not post
working application credentials, user tokens, serials, APK contents, vendor
binaries or confidential SDK documentation. Sensitive findings belong in a
private security advisory, not a public issue.
