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

DEFAULT_FILE_NAME_INPUT = "file_zero_ones_text.txt"
DEFAULT_FILE_NAME_OUTPUT = "file_encrypted.txt"
DEFAULT_FILE_NAME_BBS = "file_bbs.txt"

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="crypt.py",
        description="Szyfrator strumieniowy",
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


def load_message(filename):
    path = Path(filename)

    if not path.is_file():
        print(f"{CZERWONY}BŁĄD{RESET} Nie znaleziono pliku z wiadomością: {filename}")
        sys.exit()

    return path.read_text(encoding="utf-8").encode("utf-8")


def load_bbs_bits(filename):
    path = Path(filename)

    if not path.is_file():
        print(f"{CZERWONY}BŁĄD{RESET} Nie znaleziono pliku z ciągiem BBS: {filename}")
        sys.exit()

    bits = "".join(path.read_text(encoding="utf-8").split())

    if not bits:
        print(f"{CZERWONY}BŁĄD{RESET} Plik BBS jest pusty.")
        sys.exit()

    if any(bit not in "01" for bit in bits):
        print(f"{CZERWONY}BŁĄD{RESET} Plik BBS może zawierać wyłącznie bity 0 i 1.")
        sys.exit()

    return bits


def bits_to_bytes(bits):
    """Zamienia ciąg bitów na bajty."""
    if len(bits) % 8 != 0:
        print(f"{CZERWONY}BŁĄD{RESET} Ciąg BBS musi zawierać wielokrotność 8 bitów.")
        sys.exit()

    return bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )


def encrypt_file():
    # Wczytanie wiadomości zapisanej jako ciąg 0 i 1
    plaintext = "".join(
        Path(INPUT_FILE).read_text(encoding="ascii").split()
    )

    # Wczytanie ciągu bitów BBS
    bbs_bits = "".join(
        Path(BBS_FILE).read_text(encoding="ascii").split()
    )

    # Walidacja danych
    if not plaintext or any(bit not in "01" for bit in plaintext):
        print(f"{CZERWONY}BŁĄD{RESET} Plik wejściowy musi zawierać bity 0 i 1.")

    if not bbs_bits or any(bit not in "01" for bit in bbs_bits):
        print(f"{CZERWONY}BŁĄD{RESET} Plik BBS musi zawierać bity 0 i 1.")

    # Sprawdzenie długości klucza
    if len(bbs_bits) < len(plaintext):
        raise ValueError(
            f"Za krótki ciąg BBS: {len(bbs_bits)} bitów. "
            f"Wymagane minimum: {len(plaintext)} bitów."
        )

    # XOR bit po bicie
    ciphertext = "".join(
        str(int(m) ^ int(k))
        for m, k in zip(plaintext, bbs_bits)
    )

    # Zapis szyfrogramu jako ciągu 0 i 1
    Path(OUTPUT_FILE).write_text(ciphertext, encoding="ascii")

    print(f"{ZOLTY}INFO{RESET} Długość wiadomości: {len(plaintext)} bitów")
    print(f"{ZOLTY}INFO{RESET} Plik z BBS: {BBS_FILE}")
    print(f"{ZOLTY}INFO{RESET} Wynik zapisano w pliku: {OUTPUT_FILE}")
    print(f"{ZIELONY}OK{RESET} Plik zaszyfrowano")


if __name__ == "__main__":
    try:
        encrypt_file()
    except (OSError, ValueError) as error:
        print(f"Błąd: {error}")
