
from modes import encrypt_cbc, decrypt_cbc

key = b"0123456789ABCDEF"  # AES-128
iv = b"ABCDEF0123456789"   # 16 bajtów

message = "To jest test trybu CBC. Sprawdzamy polskie znaki: ąęłżź."

plaintext = message.encode("utf-8")

ciphertext = encrypt_cbc(plaintext, key, iv)
decrypted = decrypt_cbc(ciphertext, key, iv)

print("Wiadomość jawna:", message)
print("Szyfrogram HEX:", ciphertext.hex().upper())
print("Odszyfrowana:", decrypted.decode("utf-8"))

assert decrypted == plaintext
print("Test CBC: OK")
