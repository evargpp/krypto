from aes_ecb import encrypt_ecb, decrypt_ecb, pad_data, unpad_data

key = b"0123456789ABCDEF"  # AES-128
message = "Ala ma kota! Zażółć gęślą jaźń."

# Tekst -> bajty UTF-8 -> dopełnienie
plaintext = message.encode("utf-8")
padded = pad_data(plaintext)

# Szyfrowanie i deszyfrowanie
ciphertext = encrypt_ecb(padded, key)
decrypted_padded = decrypt_ecb(ciphertext, key)
decrypted = unpad_data(decrypted_padded)

print("Wiadomość:", message)
print("Długość przed dopełnieniem:", len(plaintext), "bajtów")
print("Długość po dopełnieniu:", len(padded), "bajtów")
print("Szyfrogram HEX:", ciphertext.hex().upper())
print("Odszyfrowana wiadomość:", decrypted.decode("utf-8"))

assert decrypted == plaintext
print("Test poprawności: OK")