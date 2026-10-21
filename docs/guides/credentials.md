# Cloud credentials and APK extraction

This guide explains how to locate the Cloud application key and P2P password
in your own copy of the Android iSIC Lite application, then enter them in
Intelbras iSIC Cloud for Home Assistant. The procedure uses static analysis;
it does not require root access, running the app, or inspecting native libraries
for the version documented here.

In the inspected build, both values are **application constants shared by
installations of that build**, not credentials issued to your individual
Intelbras account. Extracting them does not create new credentials. This
repository distributes the procedure, not the values or the vendor application.

## Credential roles

| Value | Purpose | Origin |
| --- | --- | --- |
| Cloud application key (`cloud_app_key`) | Registers the P2P client application | `ITB_P2P_KEY` in the reference APK |
| Cloud P2P password (`cloud_p2p_password`) | Used as the input to MD5 during P2P negotiation | `ITB_P2P_PASSWORD` in the reference APK |
| Recorder username/password | Authenticates RTSP after the tunnel opens | Your local account on the recorder |
| Conta Intelbras login | Used by the mobile app for account services | Not used by this integration |

Home Assistant provides password fields for both Cloud parameters, without
built-in defaults. Installing the integration does not supply these values or
obtain them through account login.

The exact server-side validation of the P2P password is not established. Earlier
experiments with an empty wire field did not establish a session, while controls
with the existing parameter decoded video. This does not establish behavior for
all firmware or service versions.

## Verified scope

The extraction was reproduced on October 21, 2026, with the following artifacts
and tools. Other versions have not been verified.

| Item | Reference |
| --- | --- |
| Application | Intelbras iSIC Lite for Android |
| Package | `com.intelbras.isiclite` |
| Version / version code | `2.8.6` / `2026041518` |
| Downloaded variant | APKPure XAPK, `armeabi-v7a` |
| Decompiler | JADX `1.5.6`, running on Java `21` |
| Signature verifier | Android `apksigner` `35.0.2` |

The assignments and their P2P call sites were confirmed in the decompiled code.
The targeted decompilation completed successfully. No new connection to a
recorder was made using the values from this APK as part of this verification.

## Prerequisites

- A copy of the iSIC Lite APK, obtained as described below.
- [JADX](https://github.com/skylot/jadx/releases/tag/v1.5.6) and a compatible Java
  runtime. Make `jadx` or `jadx-gui` available on your `PATH`.
- Android SDK [Build Tools](https://developer.android.com/tools/apksigner) for
  `apksigner` and [Command-Line Tools](https://developer.android.com/tools/apkanalyzer)
  for `apkanalyzer`.
- [Android SDK Platform Tools](https://developer.android.com/tools/adb) if you
  will copy the APK from an Android device.

The shell examples use Bash on Linux and GNU `sha256sum`. Keep APKs and
decompiled files outside your checkout of this repository:

```bash
umask 077
isic_research="$HOME/research/intelbras-isic-ha/isic-lite-local"
mkdir -p "$isic_research/apks"
cd "$isic_research"
```

## 1. Obtain the APK

### From your Android device

Install [iSIC Lite from Google Play](https://play.google.com/store/apps/details?id=com.intelbras.isiclite).
Enable USB debugging, connect the device, and authorize your computer on the
device. Confirm that ADB lists it as `device`, rather than `unauthorized`:

```bash
adb devices
```

Copy the installed APKs. Run this block in Bash; it stops if a copy fails:

```bash
(
  set -euo pipefail
  adb shell pm path com.intelbras.isiclite | tr -d '\r' > apk-paths.txt
  test -s apk-paths.txt
  while IFS= read -r line; do
    case "$line" in
      package:*) adb pull "${line#package:}" apks/ ;;
    esac
  done < apk-paths.txt
)
```

If multiple devices are connected, use `adb -s DEVICE_SERIAL` for each ADB
command. Check that every listed APK was copied. Split APKs contain additional
architecture, language, or display resources; the parameters in the verified
version were found in the base APK.

### From an APK archive

The reference build is listed on
[APKPure](https://apkpure.net/intelbras-isic-lite/com.intelbras.isiclite/download/2.8.6)
and [APKMirror](https://www.apkmirror.com/apk/intelbras-s-a/intelbras-isic-lite/intelbras-isic-lite-2-8-6-release/intelbras-isic-lite-2-8-6-android-apk-download/).
These are third-party sources. The analyzed copy was downloaded from APKPure.

If the download is an XAPK or APKM bundle, open it as a ZIP archive and extract
the APKs into `apks/`. The reference XAPK contains `com.intelbras.isiclite.apk`
and three configuration splits. You do not need to install the downloaded app
to follow this procedure.

## 2. Verify the package and signature

Set the path to the base APK. For a copy pulled from Android, the filename is
usually `apks/base.apk`; adjust this assignment accordingly:

```bash
isic_apk="$isic_research/apks/com.intelbras.isiclite.apk"
apkanalyzer apk summary "$isic_apk"
sha256sum "$isic_apk"
apksigner verify --verbose --print-certs "$isic_apk"
```

Expected package summary for the reference build:

```text
com.intelbras.isiclite 2026041518 2.8.6
```

Reference checksums:

| Artifact | SHA-256 |
| --- | --- |
| Downloaded XAPK | `06f255e028af323f97cca2c69b3f73a5d0eb8f9c5c24183ebf2e184c71e54d64` |
| Base APK | `63a2ebdc4c972753ba70113eb1815f1aff80fc215d716125868795a869bc5c4b` |
| Signer certificate | `6afefb43d7997f7b64429c43b5962a30883221b6de3e34a10a6146b058f48489` |

`apksigner verify` must succeed. The base APK and all three splits in the
reference bundle passed signature verification and used this certificate.
Its fingerprint matches the one published by the consulted mirrors; the
investigation did not independently compare it with an APK pulled from a
Google Play installation. Prefer your own installed copy as a provenance
reference when available.

A different version or bundle may have a different file hash. A file checksum
identifies exact bytes; a certificate fingerprint identifies a signing
certificate. Neither establishes that an unrelated version follows the same
extraction procedure.

## 3. Locate the application constants

Open the base APK in JADX:

```bash
jadx-gui "$isic_apk"
```

Find this fully qualified class:

```text
com.intelbras.isiclite.devices.video.dahua.P2PConnection
```

In the reference build, it is in `classes3.dex`, with the original source
identified as `P2PConnection.kt`. Open its static initializer (`static { ... }`)
and locate the string assignments to `ITB_P2P_KEY` and `ITB_P2P_PASSWORD`.

For a command-line alternative, decompile only that class:

```bash
jadx --no-res \
  --single-class com.intelbras.isiclite.devices.video.dahua.P2PConnection \
  --single-class-output P2PConnection.java \
  "$isic_apk"
```

Open the resulting `P2PConnection.java` locally. The targeted command succeeded
with JADX 1.5.6. Full-app decompilation produced unrelated partial errors and is
not required for this extraction.

Confirm the role of each constant by following its references in the same class:

| Constant | Confirmed use | Home Assistant field |
| --- | --- | --- |
| `ITB_P2P_KEY` | Third argument of `com.vveye.T2u.Init`, called by `initSDK()` | Cloud application key (`cloud_app_key`) |
| `ITB_P2P_PASSWORD` | Second argument of `com.vveye.T2u.AddPortV3`, called by `connect(...)` | Cloud P2P password (`cloud_p2p_password`) |

Copy the contents of those two string literals without quotation marks or
surrounding whitespace. Keep the values private; do not add them to source
files, shell commands, screenshots, or public issues.

Use the **original P2P password string**, not its MD5 hash. The integration
calculates the hash itself; supplying a hash would hash it again. The Conta
Intelbras login, recorder password, and TEA packet-header key are separate
values. See [Credential roles](#credential-roles) and the
[implemented protocol](../reference/protocol.md).

## 4. Configure and validate in Home Assistant

1. Open **Settings → Devices & services**.
2. Add **Intelbras iSIC Cloud**, or select **Reconfigure** on an existing entry.
3. Enter the extracted values in the two Cloud fields shown in the table above.
4. Supply your recorder's serial number, local username/password, channel count,
   stream profile, and RTSP port.
5. Submit the form, then check a snapshot and live video from a configured channel.

The form checks tunnel establishment and an authenticated RTSP `DESCRIBE` on
channel 1 before accepting the configuration. You do not need to edit Python
files. Values are stored in the private HA config entry and redacted from the
integration's diagnostics; protect the HA instance and its backups accordingly.

## Troubleshooting

| Symptom | Next step |
| --- | --- |
| ADB finds no device or reports `unauthorized` | Unlock the device, enable USB debugging, and accept the computer authorization prompt. |
| No package paths are returned | Confirm iSIC Lite is installed in the Android profile being queried. |
| Signature verification fails | Obtain another copy before continuing; do not modify or re-sign the APK to bypass the failure. |
| Class or constants are missing | Confirm the version and search JADX for `ITB_P2P_KEY`, `ITB_P2P_PASSWORD`, `AddPortV3`, or `com.vveye.T2u`; follow the actual argument flow. |
| Full-app decompilation reports errors | Try the targeted command above and inspect the relevant class. |
| HA reports a connection failure | Check the field mapping and original password string, then recorder/service availability and network connectivity. Failure alone does not identify an incorrect parameter. |
| HA reports rejected device credentials | Check the recorder's local RTSP username/password, which are separate from the Cloud parameters. |

The transport supports direct IPv4 P2P. A recorder that requires relay can work
in iSIC Lite and still fail in this integration. See
[Troubleshooting](troubleshooting.md) for transport limitations.

## Documenting another app version

Record the package/version, source, APK hashes, signer fingerprint, tools, class
and method names, and argument mapping. Report static extraction and live
connection tests separately. If values move to native code or are constructed
at runtime, a new investigation is needed; do not assume the reference
localizers still apply.

Contribute the method and non-sensitive metadata, without parameter values,
APKs, vendor libraries, decompiled vendor code, or memory/traffic dumps.

This is an independent reverse-engineering procedure, not an Intelbras
provisioning flow or endorsement. It does not change the transport's security
properties: tunneled RTSP/video is not encrypted over the internet. See
[Transport provenance](../reference/provenance.md) and [Security](../../SECURITY.md).
