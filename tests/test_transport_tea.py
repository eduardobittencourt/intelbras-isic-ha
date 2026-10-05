import pytest

from custom_components.intelbras_isic.transport.tea import (
    decrypt,
    decrypt_block,
    encrypt,
    encrypt_block,
)


def test_standard_zero_vector():
    expected = bytes.fromhex("0a3aea4140a9ba94")
    assert encrypt_block(bytes(8), bytes(16)) == expected
    assert decrypt_block(expected, bytes(16)) == bytes(8)


def test_multiblock_and_padding():
    message = b"synthetic protocol payload"
    key = bytes(range(16))
    encoded = encrypt(message, key)
    assert len(encoded) % 8 == 0
    assert decrypt(encoded, key) == message + b"\0" * (-len(message) % 8)


@pytest.mark.parametrize("data,key", [(bytes(7), bytes(16)), (bytes(8), bytes(15))])
def test_invalid_lengths(data, key):
    with pytest.raises(ValueError):
        decrypt(data, key)
