from sympy import randprime
from math import gcd
import secrets
from datetime import datetime
from pathlib import Path
import argparse
import sys

PRIME_BITS = 32

CZERWONY = "\033[31m"
ZIELONY = "\033[32m"
ZOLTY = "\033[33m"
RESET = "\033[0m"

def generate_blum_prime(bits=256):
    """Generuje liczbę pierwszą p, dla której p % 4 == 3."""
    while True:
        p = randprime(2**(bits - 1), 2**bits)
        if p % 4 == 3:
            return p


from datetime import datetime

def save_bits_to_file(bits, filename="bbs_output.txt"):

    bit_string = "".join(map(str, bits))

    with open(filename, "w", encoding="utf-8") as file:
        file.write(bit_string)

    print(f"{ZOLTY}INFO{RESET} Zapisano {len(bits)} bitów do pliku: {filename}")

    return filename

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="bbs_generator.py",
        description="Generator BBS",
        epilog="Projekt zaliczeniowy Podstawy kryptografii, Bartosz Grabski 59233 '2026"

    )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_filename = f"bbs_output_{timestamp}.txt"

    parser.add_argument(
        "-o", "--output",
        type=str,
        default = full_filename,
        help="Plik TXT zawierający ciąg binarny 0/1 (domyślnie: bbs_output_{timestamp}.txt)"
    )

    parser.add_argument(
        "-c", "--count",
        type=int,
        default=20000,
        help="Liczba bitów do wygenerowania (domylśnie 20000)"
    )

    parser.add_argument(
        "-p",
        type=int,
        default=generate_blum_prime(PRIME_BITS),
        help="Liczba p (domylśnie generuje liczbę pierwszą losowo 32bit)"
    )

    parser.add_argument(
        "-q",
        type=int,
        default=generate_blum_prime(PRIME_BITS),
        help="Liczba q (domylśnie generuje liczbę pierwszą losowo 32bit)"
    )


    return parser.parse_args()


args = parse_arguments()

bit_count = args.count

# p = generate_blum_prime(prime_bits)
# q = generate_blum_prime(prime_bits)

p = args.p
q = args.q

while p == q or gcd(p, q) != 1:
    print(f"{ZOLTY}INFO{RESET} Wyznaczam nowe q, bo nie spełniało gcd.")
    q = generate_blum_prime(PRIME_BITS)

print(f"{ZOLTY}INFO{RESET} Liczba p: {p}.")
print(f"{ZOLTY}INFO{RESET} Liczba q: {q}.")

n = p * q

print(f"{ZOLTY}INFO{RESET} Liczba n=p*q: {n}.")

while True:
    a = secrets.randbelow(n - 2)
    if gcd(a, n) == 1:
        break

x = pow(a, 2, n)
bits = []

for _ in range(bit_count):
    x = pow(x, 2, n)
    bits.append(str(x % 2))

save_bits_to_file(bits, args.output)
