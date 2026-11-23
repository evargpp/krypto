from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

BLOCK_SIZE = 16  # AES ma blok o długości 128 bitów


def encrypt_ecb(data: bytes, key: bytes) -> bytes:
    """Szyfruje dane AES-ECB. Dane muszą być pełnymi blokami."""
    if len(key) not in (16, 24, 32):
        raise ValueError("Klucz AES musi mieć 16, 24 lub 32 bajty.")

    if len(data) % BLOCK_SIZE != 0:
        raise ValueError("Dane muszą mieć długość będącą wielokrotnością 16 bajtów.")

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()

    return encryptor.update(data) + encryptor.finalize()


def decrypt_ecb(data: bytes, key: bytes) -> bytes:
    """Deszyfruje dane AES-ECB. Dane muszą być pełnymi blokami."""
    if len(key) not in (16, 24, 32):
        raise ValueError("Klucz AES musi mieć 16, 24 lub 32 bajty.")

    if len(data) == 0 or len(data) % BLOCK_SIZE != 0:
        raise ValueError("Szyfrogram musi zawierać pełne bloki AES.")

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = cipher.decryptor()

    return decryptor.update(data) + decryptor.finalize()


def pad_data(data: bytes) -> bytes:
    """Dopełnia dane zgodnie ze standardem PKCS#7."""
    padder = PKCS7(BLOCK_SIZE * 8).padder()
    return padder.update(data) + padder.finalize()


def unpad_data(data: bytes) -> bytes:
    """Usuwa dopełnienie PKCS#7."""
    unpadder = PKCS7(BLOCK_SIZE * 8).unpadder()
    return unpadder.update(data) + unpadder.finalize()

