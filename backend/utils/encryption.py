# /Users/1byinf8/Documents/quant-api/utils/encryption.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import hashlib

def encrypt_file(key, input_file, output_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found!")
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    with open(input_file, 'rb') as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    with open(output_file, 'wb') as f:
        f.write(nonce + ciphertext)
    return hashlib.sha256(ciphertext).digest()

def decrypt_file(key, encrypted_file, output_file):
    if not os.path.exists(encrypted_file):
        raise FileNotFoundError(f"Encrypted file '{encrypted_file}' not found!")
    with open(encrypted_file, 'rb') as f:
        data = f.read()
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    with open(output_file, 'wb') as f:
        f.write(plaintext)
    return hashlib.sha256(ciphertext).digest()