from Crypto.Cipher import AES

ROZMIAR_BLOKU = 16  # 128 bitów

# Kolory ANSI do naprzemiennego wyróżniania bloków w terminalu
KOLORY = ["\033[94m", "\033[92m", "\033[93m", "\033[95m", "\033[96m"]
RESET = "\033[0m"


# =====================================================================
# CZARNA SKRZYNKA: Pojedynczy blok AES w trybie ECB
# =====================================================================
def szyfruj_blok_ecb(blok, klucz):
    cipher = AES.new(klucz, AES.MODE_ECB)
    return cipher.encrypt(blok)


def deszyfruj_blok_ecb(blok, klucz):
    cipher = AES.new(klucz, AES.MODE_ECB)
    return cipher.decrypt(blok)


# =====================================================================
# POMOCNICZE: XOR oraz dopełnianie (PKCS#7)
# =====================================================================
def xor_bajtow(a, b):
    wynik = bytearray()
    for x, y in zip(a, b):
        wynik.append(x ^ y)
    return bytes(wynik)


def dopelnij_pkcs7(dane):
    brakujace = ROZMIAR_BLOKU - (len(dane) % ROZMIAR_BLOKU)
    return dane + bytes([brakujace] * brakujace)


def usun_dopelnienie_pkcs7(dane):
    if not dane:
        return dane
    ostatni_bajt = dane[-1]
    # Jeśli wartość ostatniego bajtu ma sens jako padding PKCS#7, usuwamy go
    if 1 <= ostatni_bajt <= ROZMIAR_BLOKU and dane[-ostatni_bajt:] == bytes([ostatni_bajt] * ostatni_bajt):
        return dane[:-ostatni_bajt]
    return dane


# =====================================================================
# IMPLEMENTACJA TRYBÓW PRACY
# =====================================================================
def szyfruj_ecb(dane, klucz):
    dane_pad = dopelnij_pkcs7(dane)
    wynik = bytearray()
    for i in range(0, len(dane_pad), ROZMIAR_BLOKU):
        blok = dane_pad[i : i + ROZMIAR_BLOKU]
        wynik.extend(szyfruj_blok_ecb(blok, klucz))
    return bytes(wynik)


def deszyfruj_ecb(szyfrogram, klucz):
    wynik = bytearray()
    for i in range(0, len(szyfrogram), ROZMIAR_BLOKU):
        blok = szyfrogram[i : i + ROZMIAR_BLOKU]
        if len(blok) == ROZMIAR_BLOKU:
            wynik.extend(deszyfruj_blok_ecb(blok, klucz))
        else:
            wynik.extend(b"?" * len(blok))  # Niepełny blok po uszkodzeniu
    return usun_dopelnienie_pkcs7(bytes(wynik))


def szyfruj_cbc(dane, klucz, iv):
    dane_pad = dopelnij_pkcs7(dane)
    wynik = bytearray()
    poprzedni_blok = iv
    for i in range(0, len(dane_pad), ROZMIAR_BLOKU):
        blok = dane_pad[i : i + ROZMIAR_BLOKU]
        wejscie_ecb = xor_bajtow(blok, poprzedni_blok)
        zaszyfrowany = szyfruj_blok_ecb(wejscie_ecb, klucz)
        wynik.extend(zaszyfrowany)
        poprzedni_blok = zaszyfrowany
    return bytes(wynik)


def deszyfruj_cbc(szyfrogram, klucz, iv):
    wynik = bytearray()
    poprzedni_blok = iv
    for i in range(0, len(szyfrogram), ROZMIAR_BLOKU):
        blok = szyfrogram[i : i + ROZMIAR_BLOKU]
        if len(blok) == ROZMIAR_BLOKU:
            odszyfrowany_ecb = deszyfruj_blok_ecb(blok, klucz)
            wynik.extend(xor_bajtow(odszyfrowany_ecb, poprzedni_blok))
            poprzedni_blok = blok
        else:
            wynik.extend(b"?" * len(blok))
    return usun_dopelnienie_pkcs7(bytes(wynik))


def szyfruj_ctr(dane, klucz, nonce_int):
    # W CTR nie jest wymagany padding!
    wynik = bytearray()
    licznik = nonce_int
    for i in range(0, len(dane), ROZMIAR_BLOKU):
        blok = dane[i : i + ROZMIAR_BLOKU]
        # Zamiana licznika na 16-bajtowy blok wejściowy
        blok_licznika = licznik.to_bytes(ROZMIAR_BLOKU, byteorder="big")
        strumien_klucza = szyfruj_blok_ecb(blok_licznika, klucz)
        wynik.extend(xor_bajtow(blok, strumien_klucza[: len(blok)]))
        licznik += 1
    return bytes(wynik)


def deszyfruj_ctr(szyfrogram, klucz, nonce_int):
    # Deszyfrowanie w CTR jest identyczne jak szyfrowanie
    return szyfruj_ctr(szyfrogram, klucz, nonce_int)


# =====================================================================
# FUNKCJA WYŚWIETLAJĄCA BLOKI (KOLORY, HEX, BITY, TEKST)
# =====================================================================
def wyswietl_bloki(tytul, dane, pokaz_bity=False):
    print(f"\n--- {tytul} (długość: {len(dane)} B) ---")
    hex_bloki = []
    bit_bloki = []
    tekst_bloki = []

    for idx, i in enumerate(range(0, len(dane), ROZMIAR_BLOKU)):
        blok = dane[i : i + ROZMIAR_BLOKU]
        kolor = KOLORY[idx % len(KOLORY)]

        hex_str = " ".join(f"{b:02X}" for b in blok)
        hex_bloki.append(f"{kolor}[B{idx}: {hex_str}]{RESET}")

        tekst = "".join(chr(b) if 32 <= b <= 126 else "." for b in blok)
        tekst_bloki.append(f"{kolor}{tekst}{RESET}")

        if pokaz_bity:
            bity = " ".join(f"{b:08b}" for b in blok[:4]) + " ..."
            bit_bloki.append(f"{kolor}[B{idx}: {bity}]{RESET}")

    print("TEKST: " + " | ".join(tekst_bloki))
    print("HEX  : " + " ".join(hex_bloki))
    if pokaz_bity:
        print("BITY : " + " ".join(bit_bloki))


# =====================================================================
# FUNKCJE MODYFIKUJĄCE SZYFROGRAM (Zadanie 7: a-f)
# =====================================================================
def modyfikacje_szyfrogramu(szyfrogram):
    b = bytearray(szyfrogram)
    wyniki = {}

    # a) Usunąć cały blok (usuwamy blok nr 1, czyli bajty 16..31)
    wyniki["a) Usunięcie całego bloku (B1)"] = bytes(b[:16] + b[32:])

    # b) Powielić wybrany blok (powielamy blok nr 1)
    wyniki["b) Powielenie wybranego bloku (B1)"] = bytes(b[:16] + b[16:32] + b[16:])

    # c) Zamienić bloki miejscami (zamiana B1 z B2)
    wyniki["c) Zamiana bloków miejscami (B1 <-> B2)"] = bytes(b[:16] + b[32:48] + b[16:32] + b[48:])

    # d) Zmienić wartość jednego bitu w bloku (odwrócenie 1 bitu w bloku B1, bajt 16)
    b_bit = bytearray(szyfrogram)
    b_bit[16] ^= 0b00000001
    wyniki["d) Zmiana 1 bitu w bloku B1"] = bytes(b_bit)

    # e) Zamienić wewnątrz bloku bajty miejscami (w bloku B1 zamieniamy bajt 16 i 17)
    b_swap = bytearray(szyfrogram)
    b_swap[16], b_swap[17] = b_swap[17], b_swap[16]
    wyniki["e) Zamiana bajtów wewnątrz bloku B1"] = bytes(b_swap)

    # f) Usunąć fragment bloku (usuwamy 1 bajt z bloku B1 - indeks 16)
    wyniki["f) Usunięcie 1 bajtu z bloku B1"] = bytes(b[:16] + b[17:])

    return wyniki


# =====================================================================
# GŁÓWNY PROGRAM
# =====================================================================
def main():
    print("=== KONFIGURACJA PARAMETRÓW SZYFROWANIA ===")
    klucz_str = input("Podaj 16-znakowy klucz [Enter = 'TajnyKlucz123456']: ") or "TajnyKlucz123456"
    klucz = klucz_str.encode("utf-8")[:16].ljust(16, b"0")

    iv_str = input("Podaj 16-znakowy wektor IV dla CBC [Enter = 'WektorStartowy01']: ") or "WektorStartowy01"
    iv = iv_str.encode("utf-8")[:16].ljust(16, b"0")

    nonce_wejscie = input("Podaj liczbę początkową Nonce dla CTR [Enter = 1000]: ") or "1000"
    nonce = int(nonce_wejscie)

    # Punkt 9: Trzy rodzaje wiadomości wejściowych (każda ma min. 4 bloki = 64 bajty)
    wiadomosci_testowe = {
        "1. Jednakowe znaki":
    ,
        "2. Kolejne znaki alfabetu": b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz!@",
        "3. Prosty znany tekst": b"To jest tajna wiadomosc testowa przygotowana na zajecia z krypto",
    }

    for nazwa_testu, tekst_jawny in wiadomosci_testowe.items():
        print("\n" + "=" * 80)
        print(f"BADANIE DLA WIADOMOŚCI: {nazwa_testu}")
        print("=" * 80)

        wyswietl_bloki("Wiadomość jawna (oryginał)", tekst_jawny, pokaz_bity=True)

        # Szyfrowanie we wszystkich trybach (Punkt 6)
        szyfrogramy = {
            "ECB": szyfruj_ecb(tekst_jawny, klucz),
            "CBC": szyfruj_cbc(tekst_jawny, klucz, iv),
            "CTR": szyfruj_ctr(tekst_jawny, klucz, nonce),
        }

        for tryb, szyfrogram in szyfrogramy.items():
            print(f"\n>>> TRYB {tryb} <<<")
            wyswietl_bloki(f"Szyfrogram ({tryb})", szyfrogram, pokaz_bity=False)

            # Weryfikacja poprawnego deszyfrowania
            if tryb == "ECB":
                odszyfrowany = deszyfruj_ecb(szyfrogram, klucz)
            elif tryb == "CBC":
                odszyfrowany = deszyfruj_cbc(szyfrogram, klucz, iv)
            else:
                odszyfrowany = deszyfruj_ctr(szyfrogram, klucz, nonce)

            poprawnosc = "TAK" if odszyfrowany == tekst_jawny else "NIE"
            print(f"Weryfikacja deszyfrowania bez modyfikacji: {poprawnosc}")

            # Modyfikacje szyfrogramu (Punkty 7 i 8)
            print("\n--- Wyniki deszyfrowania po modyfikacjach (Zadanie 7 i 8) ---")
            for opis_mod, zmodyfikowany_szyfrogram in modyfikacje_szyfrogramu(szyfrogram).items():
                if tryb == "ECB":
                    wynik_mod = deszyfruj_ecb(zmodyfikowany_szyfrogram, klucz)
                elif tryb == "CBC":
                    wynik_mod = deszyfruj_cbc(zmodyfikowany_szyfrogram, klucz, iv)
                else:
                    wynik_mod = deszyfruj_ctr(zmodyfikowany_szyfrogram, klucz, nonce)

                czytelny = "".join(chr(b) if 32 <= b <= 126 else "." for b in wynik_mod)
                print(f"{opis_mod:<42} -> {czytelny}")


if __name__ == "__main__":
    main()