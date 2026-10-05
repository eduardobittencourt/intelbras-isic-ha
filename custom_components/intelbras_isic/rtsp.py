"""Small RTSP Digest probe used during setup."""

from __future__ import annotations

import asyncio
import hashlib
import re
import secrets


class RtspError(Exception):
    """RTSP request failed."""


class RtspAuthError(RtspError):
    """The device rejected its RTSP credentials."""


def _digest_value(value: str) -> str:
    return hashlib.md5(value.encode(), usedforsecurity=False).hexdigest()


def _parse_challenge(header: str) -> dict[str, str]:
    if not header.lower().startswith("digest "):
        raise RtspAuthError("The device did not offer Digest authentication")
    return {
        key.lower(): value
        for key, quoted, bare in re.findall(
            r'(\w+)=(?:"([^"]*)"|([^,\s]+))', header[7:]
        )
        if (value := quoted or bare)
    }


async def _exchange(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    url: str,
    sequence: int,
    authorization: str | None = None,
) -> tuple[int, dict[str, str], bytes]:
    lines = [
        f"DESCRIBE {url} RTSP/1.0",
        f"CSeq: {sequence}",
        "Accept: application/sdp",
        "User-Agent: Home Assistant Intelbras iSIC",
    ]
    if authorization:
        lines.append(f"Authorization: {authorization}")
    writer.write(("\r\n".join(lines) + "\r\n\r\n").encode())
    await writer.drain()
    raw_headers = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=10)
    header_text = raw_headers.decode("latin-1")
    header_lines = header_text.split("\r\n")
    status = int(header_lines[0].split()[1])
    headers: dict[str, str] = {}
    for line in header_lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    body = (
        await asyncio.wait_for(reader.readexactly(length), timeout=10)
        if length
        else b""
    )
    return status, headers, body


async def async_probe(url: str, username: str, password: str) -> None:
    """Verify RTSP credentials and ensure the selected stream contains video."""
    match = re.match(r"rtsp://([^:/]+):(\d+)(/.*)", url)
    if match is None:
        raise RtspError("Invalid RTSP URL")
    host, port, _path = match.groups()
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, int(port)), timeout=10
    )
    try:
        status, headers, body = await _exchange(reader, writer, url, 1)
        if status != 401:
            if status == 200 and b"m=video" in body:
                return
            raise RtspError(f"Unexpected RTSP status {status}")

        challenge = _parse_challenge(headers.get("www-authenticate", ""))
        realm = challenge.get("realm", "")
        nonce = challenge.get("nonce", "")
        if not realm or not nonce:
            raise RtspAuthError("Incomplete Digest authentication challenge")
        offered_qop = [item.strip() for item in challenge.get("qop", "").split(",")]
        qop = "auth" if "auth" in offered_qop else ""
        cnonce = secrets.token_hex(8)
        nc = "00000001"
        ha1 = _digest_value(f"{username}:{realm}:{password}")
        ha2 = _digest_value(f"DESCRIBE:{url}")
        response = (
            _digest_value(f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}")
            if qop
            else _digest_value(f"{ha1}:{nonce}:{ha2}")
        )
        fields = [
            f'username="{username}"',
            f'realm="{realm}"',
            f'nonce="{nonce}"',
            f'uri="{url}"',
            f'response="{response}"',
            "algorithm=MD5",
        ]
        if qop:
            fields.extend((f"qop={qop}", f"nc={nc}", f'cnonce="{cnonce}"'))
        if opaque := challenge.get("opaque"):
            fields.append(f'opaque="{opaque}"')

        status, _headers, body = await _exchange(
            reader, writer, url, 2, "Digest " + ", ".join(fields)
        )
        if status == 401:
            raise RtspAuthError("Invalid device username or password")
        if status != 200:
            raise RtspError(f"Unexpected authenticated RTSP status {status}")
        if b"m=video" not in body:
            raise RtspError("The RTSP endpoint did not return a video stream")
    finally:
        writer.close()
        await writer.wait_closed()
