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

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="zeroones2ascii.py",
        description="Konwerter pliku tekstowego zwierającego zera i jedynki na plik tekstowy ascii",
        epilog="Projekt zaliczeniowy Podstawy kryptografii, Bartosz Grabski 59233 '2026"
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        default = 'file_zero_ones_text.txt',
        help="Plik TXT zawierający ciąg zero jedynkowy do zamiany"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default = 'file_plain_text_converted.txt',
        help="Plik TXT zawierający zdekodowany ciąg ascii"
    )

    return parser.parse_args()


def binary_to_ascii(input_file, output_file):
    input_path = Path(input_file)

    if not input_path.is_file():
        print(f"{CZERWONY}BŁĄD{RESET} Nie znaleziono pliku: {input_file}.")
        sys.exit()

    # Wczytanie ciągu bitów
    bits = "".join(input_path.read_text(encoding="ascii").split())

    if not bits:
        print(f"{CZERWONY}BŁĄD{RESET} Plik wejściowy jest pusty.")
        sys.exit()

    if any(bit not in "01" for bit in bits):
        print(f"{CZERWONY}BŁĄD{RESET} Plik może zawierać wyłącznie bity 0 i 1.")
        sys.exit()

    if len(bits) % 8 != 0:
        print(f"{CZERWONY}BŁĄD{RESET} Długość ciągu ({len(bits)} bitów) nie jest wielokrotnością 8.")
        sys.exit()

    # Zamiana każdej grupy 8 bitów na bajt
    data = bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )

    # Odtworzenie tekstu UTF-8
    text = data.decode("utf-8")

    # Zapis do pliku
    Path(output_file).write_text(text, encoding="utf-8")

    print(f"{ZOLTY}INFO{RESET} Plik wejściowy: {input_file}")
    print(f"{ZOLTY}INFO{RESET} Liczba bajtów: {len(data)}")
    print(f"{ZOLTY}INFO{RESET} Liczba bitów: {len(bits)}")
    print(f"{ZOLTY}INFO{RESET} Zapisano wynik do: {output_file}")
    print(f"{ZIELONY}OK{RESET} Poprawnie skonwertowano")


if __name__ == "__main__":
    args = parse_arguments()
    INPUT_FILE = args.input
    OUTPUT_FILE = args.output

    binary_to_ascii(INPUT_FILE, OUTPUT_FILE)
