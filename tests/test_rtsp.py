"""Tests for the small RTSP Digest client."""

import pytest

from custom_components.intelbras_isic.rtsp import RtspAuthError, _parse_challenge


def test_parse_digest_challenge_without_qop() -> None:
    """Older Intelbras recorders omit qop in their Digest challenge."""
    challenge = _parse_challenge(
        'Digest realm="Login to device", nonce="abc123", algorithm=MD5'
    )

    assert challenge == {
        "realm": "Login to device",
        "nonce": "abc123",
        "algorithm": "MD5",
    }


def test_reject_non_digest_challenge() -> None:
    """Only Digest authentication is supported."""
    with pytest.raises(RtspAuthError):
        _parse_challenge('Basic realm="camera"')
