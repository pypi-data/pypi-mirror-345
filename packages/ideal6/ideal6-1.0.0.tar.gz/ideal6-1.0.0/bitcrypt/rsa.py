from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def generate_keys():
    key = RSA.generate(2048)
    return key.export_key(), key.publickey().export_key()

def encrypt_key(public_key_bytes: bytes, secret_key: bytes) -> bytes:
    recipient_key = RSA.import_key(public_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    return cipher_rsa.encrypt(secret_key)

def decrypt_key(private_key_bytes: bytes, encrypted_key: bytes) -> bytes:
    private_key = RSA.import_key(private_key_bytes)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    return cipher_rsa.decrypt(encrypted_key)