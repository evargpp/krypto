import os
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# 1. Przygotowanie plików testowych (1 MB, 10 MB, 50 MB)
rozmiary = {
    "maly_1MB.bin": 1 * 1024 * 1024,
    "sredni_10MB.bin": 10 * 1024 * 1024,
    "duzy_50MB.bin": 50 * 1024 * 1024,
}

print("Generowanie plików testowych...")
for nazwa, rozmiar in rozmiary.items():
    with open(nazwa, "wb") as f:
        f.write(os.urandom(rozmiar))

klucz = get_random_bytes(16)  # Klucz AES-128 (16 bajtów)
iv = get_random_bytes(16)  # Wektor inicjujący (16 bajtów)
nonce = get_random_bytes(8)  # Licznik początkowy dla CTR (8 bajtów)

tryby = ["ECB", "CBC", "CFB", "OFB", "CTR"]


def utworz_szyfr(tryb):
    if tryb == "ECB":
        return AES.new(klucz, AES.MODE_ECB)
    elif tryb == "CBC":
        return AES.new(klucz, AES.MODE_CBC, iv=iv)
    elif tryb == "CFB":
        return AES.new(klucz, AES.MODE_CFB, iv=iv)
    elif tryb == "OFB":
        return AES.new(klucz, AES.MODE_OFB, iv=iv)
    elif tryb == "CTR":
        return AES.new(klucz, AES.MODE_CTR, nonce=nonce)


print("\nRozpoczynam pomiary (czasy w sekundach):\n")
print(f"{'Plik':<16} | {'Tryb':<5} | {'Szyfrowanie [s]':<16} | {'Deszyfrowanie [s]':<16}")
print("-" * 62)

for nazwa in rozmiary.keys():
    with open(nazwa, "rb") as f:
        dane = f.read()

    for tryb in tryby:
        # Pomiar szyfrowania
        szyfr_enc = utworz_szyfr(tryb)
        start = time.perf_counter()
        if tryb in ["ECB", "CBC"]:
            szyfrogram = szyfr_enc.encrypt(pad(dane, 16))
        else:
            szyfrogram = szyfr_enc.encrypt(dane)
        czas_enc = time.perf_counter() - start

        # Pomiar deszyfrowania
        szyfr_dec = utworz_szyfr(tryb)
        start = time.perf_counter()
        if tryb in ["ECB", "CBC"]:
            odszyfrowane = unpad(szyfr_dec.decrypt(szyfrogram), 16)
        else:
            odszyfrowane = szyfr_dec.decrypt(szyfrogram)
        czas_dec = time.perf_counter() - start

        print(f"{nazwa:<16} | {tryb:<5} | {czas_enc:<16.5f} | {czas_dec:<16.5f}")
    print("-" * 62)

# Sprzątanie plików tymczasowych
for nazwa in rozmiary.keys():
    os.remove(nazwa)