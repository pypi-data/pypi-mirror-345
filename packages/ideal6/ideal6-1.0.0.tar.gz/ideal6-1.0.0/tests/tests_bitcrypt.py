from bitcrypt.core import BitCrypt

def test_encryption_decryption():
    bc = BitCrypt()
    data = b"Test message 1234"
    encrypted = bc.encrypt(data)
    decrypted = bc.decrypt(encrypted)
    assert decrypted == data

def test_empty_data():
    bc = BitCrypt()
    data = b""
    encrypted = bc.encrypt(data)
    decrypted = bc.decrypt(encrypted)
    assert decrypted == data

def test_invalid_ciphertext():
    bc = BitCrypt()
    try:
        bc.decrypt(b"short")
        assert False, "Expected ValueError"
    except ValueError:
        assert True