from sympy import randprime
from math import gcd
import secrets
from datetime import datetime
from pathlib import Path
import argparse
import sys

CZERWONY = "\033[31m"
ZIELONY = "\033[32m"
ZOLTY = "\033[33m"
RESET = "\033[0m"

DEFAULT_FILE_NAME_INPUT = "file_encrypted.txt"
DEFAULT_FILE_NAME_OUTPUT = "file_zero_ones_text_decrypted.txt"
DEFAULT_FILE_NAME_BBS = "file_bbs.txt"

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="decrypt.py",
        description="Deszyfrator strumieniowy",
        epilog="Projekt zaliczeniowy Podstawy kryptografii, Bartosz Grabski 59233 '2026"
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        default = DEFAULT_FILE_NAME_INPUT,
        help=F"Plik TXT zawierający ciąg 0/1 do zaszyfrowania (domyślnie {DEFAULT_FILE_NAME_INPUT})"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default = DEFAULT_FILE_NAME_OUTPUT,
        help=f"Plik TXT zawierający ciąg 0/1 zaszyfrowany (domyślnie {DEFAULT_FILE_NAME_OUTPUT})"
    )

    parser.add_argument(
        "-b", "--bbs",
        type=str,
        default = DEFAULT_FILE_NAME_BBS,
        help=f"Plik TXT zawierający ciąg szyfrujący (domyślnie {DEFAULT_FILE_NAME_BBS})"
    )
    return parser.parse_args()

def xor_bytes(data, key):
    if len(data) != len(key):
        print(f"{CZERWONY}BŁĄD{RESET} Wiadomość i klucz muszą mieć tę samą długość")
        sys.exit()

    return bytes(a ^ b for a, b in zip(data, key))


args = parse_arguments()

INPUT_FILE = args.input
BBS_FILE = args.bbs
OUTPUT_FILE = args.output

def decrypt_file():
    # Wczytanie szyfrogramu

    path = Path(INPUT_FILE)
    if not path.is_file():
        print(f"{CZERWONY}BŁĄD{RESET} Nie znaleziono pliku z wiadomością: {INPUT_FILE}")
        sys.exit()

    ciphertext = "".join(
        Path(INPUT_FILE).read_text(encoding="ascii").split()
    )

    path = Path(BBS_FILE)
    if not path.is_file():
        print(f"{CZERWONY}BŁĄD{RESET} Nie znaleziono pliku z wiadomością: {BBS_FILE}")
        sys.exit()

    # Wczytanie klucza BBS
    bbs_bits = "".join(
        Path(BBS_FILE).read_text(encoding="ascii").split()
    )

    # Walidacja danych
    if not ciphertext or any(bit not in "01" for bit in ciphertext):
        print(f"{CZERWONY}BŁĄD{RESET} Plik zaszyfrowany musi zawierać bity 0 i 1.")
        sys.exit()

    if not bbs_bits or any(bit not in "01" for bit in bbs_bits):
        print(f"{CZERWONY}BŁĄD{RESET} Plik BBS musi zawierać bity 0 i 1.")
        sys.exit()

    # Sprawdzenie długości klucza
    if len(bbs_bits) < len(ciphertext):
        print(f"{CZERWONY}BŁĄD{RESET} Klucz BBS jest za krótki: {len(bbs_bits)} bitów. Wymagane minimum: {len(ciphertext)} bitów.")
        sys.exit()

    # Deszyfrowanie XOR
    plaintext = "".join(
        str(int(c) ^ int(k))
        for c, k in zip(ciphertext, bbs_bits)
    )

    # Zapis odszyfrowanej wiadomości jako ciągu bitów
    Path(OUTPUT_FILE).write_text(
        plaintext,
        encoding="ascii"
    )

    print(f"{ZOLTY}INFO{RESET} Długość szyfrogramu: {len(ciphertext)} bitów")
    print(f"{ZOLTY}INFO{RESET} Wykorzystano bitów BBS: {len(ciphertext)}")
    print(f"{ZOLTY}INFO{RESET} Odszyfrowany wynik zapisano w: {OUTPUT_FILE}")
    print(f"{ZIELONY}OK{RESET} Plik odszyfrowano")


if __name__ == "__main__":
    try:
        decrypt_file()
    except (OSError, ValueError) as error:
        print(f"Błąd: {error}")