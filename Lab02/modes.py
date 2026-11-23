
from aes_ecb import (
    encrypt_ecb,
    decrypt_ecb,
    pad_data,
    unpad_data,
    BLOCK_SIZE,
)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """Wykonuje XOR na dwóch ciągach bajtów tej samej długości."""
    if len(a) != len(b):
        raise ValueError("Dane do XOR muszą mieć tę samą długość.")

    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    """Szyfruje dane w trybie CBC."""
    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV musi mieć dokładnie 16 bajtów.")

    padded = pad_data(plaintext)
    ciphertext = bytearray()
    previous_block = iv

    for i in range(0, len(padded), BLOCK_SIZE):
        block = padded[i:i + BLOCK_SIZE]

        # CBC: XOR bloku jawnego z IV lub poprzednim szyfrogramem
        block_xor = xor_bytes(block, previous_block)

        # Szyfrujemy pojedynczy blok za pomocą AES
        encrypted_block = encrypt_ecb(block_xor, key)

        ciphertext.extend(encrypted_block)
        previous_block = encrypted_block

    return bytes(ciphertext)


def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """Deszyfruje dane w trybie CBC."""
    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV musi mieć dokładnie 16 bajtów.")

    if len(ciphertext) == 0 or len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Szyfrogram musi zawierać pełne bloki AES.")

    plaintext = bytearray()
    previous_block = iv

    for i in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[i:i + BLOCK_SIZE]

        # Najpierw odszyfrowujemy blok
        decrypted_block = decrypt_ecb(block, key)

        # Następnie XOR z IV lub poprzednim blokiem szyfrogramu
        plaintext_block = xor_bytes(decrypted_block, previous_block)

        plaintext.extend(plaintext_block)
        previous_block = block

    return unpad_data(bytes(plaintext))
