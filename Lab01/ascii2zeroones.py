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

DEFAULT_FILE_NAME_INPUT = "file_plain_text.txt"
DEFAULT_FILE_NAME_OUTPUT = "file_zero_ones_text.txt"
DEFAULT_FILE_NAME_BBS = "file_bbs.txt"

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="ascii2zeroones.py",
        description="Konwerter pliku tekstowego ASCII na plik tekstowy zwierający zera i jedynki",
        epilog="Projekt zaliczeniowy Podstawy kryptografii, Bartosz Grabski 59233 '2026"

    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        default = DEFAULT_FILE_NAME_INPUT,
        help=f"Plik TXT zawierający ciąg do zamiany (domyślnie {DEFAULT_FILE_NAME_INPUT})"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default = DEFAULT_FILE_NAME_OUTPUT,
        help=f"Plik TXT zawierający ciąg zero jedynkowy (domyślnie {DEFAULT_FILE_NAME_OUTPUT})"
    )

    return parser.parse_args()


def ascii_to_binary(input_file, output_file):
    input_path = Path(input_file)

    if not input_path.is_file():
        print(f"{CZERWONY}BŁĄD{RESET} Nie znaleziono pliku: {input_file}")
        sys.exit()

    # Odczyt danych jako bajtów
    data = input_path.read_bytes()

    # Każdy bajt zamieniamy na 8 bitów
    binary = "".join(f"{byte:08b}" for byte in data)

    # Zapis ciągu bitów
    Path(output_file).write_text(binary, encoding="ascii")

    print(f"{ZOLTY}INFO{RESET} Plik wejściowy: {input_file}")
    print(f"{ZOLTY}INFO{RESET} Liczba bajtów: {len(data)}")
    print(f"{ZOLTY}INFO{RESET} Liczba bitów: {len(binary)}")
    print(f"{ZOLTY}INFO{RESET} Zapisano wynik do: {output_file}")
    print(f"{ZIELONY}OK{RESET} Poprawnie skonwertowano")


if __name__ == "__main__":
    args = parse_arguments()
    INPUT_FILE = args.input
    OUTPUT_FILE = args.output

    ascii_to_binary(INPUT_FILE, OUTPUT_FILE)
