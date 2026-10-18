from pathlib import Path
import argparse
import sys

CZERWONY = "\033[31m"
ZIELONY = "\033[32m"
ZOLTY = "\033[33m"
RESET = "\033[0m"

DOPUSZCZALNA_LICZBA_JEDYNEK_MIN = 9725
DOPUSZCZALNA_LICZBA_JEDYNEK_MAX = 10275

LIMITS = [
    (2315, 2685),
    (1114, 1386),
    (527, 723),
    (240, 384),
    (103, 209),
    (103, 209)
]


def validate_bits(bits):
    """Sprawdza, czy wejście zawiera wyłącznie bity 0 i 1."""

    if isinstance(bits, str):
        bits = "".join(bits.split())
    else:
        bits = "".join(map(str, bits))

    if not bits:
        print(f"{CZERWONY}BŁĄD{RESET} Ciąg wejściowy jest pusty.")
        sys.exit()

    if any(bit not in "01" for bit in bits):
        print(f"{CZERWONY}BŁĄD{RESET} Ciąg może zawierać wyłącznie znaki 0 i 1.")
        sys.exit()

    return bits


def prepare_bits(bits, mode="truncate", start=0):
    """
    Przygotowuje ciąg o długości TEST_LENGTH.

    mode:
        truncate  - bierze pierwsze 20000 bitów,
        substring - pobiera 20000 bitów od pozycji start.
    """

    bits = validate_bits(bits)

    if len(bits) < TEST_LENGTH:
        print(f"{CZERWONY}BŁĄD{RESET} Ciąg jest za krótki: {len(bits)} bitów.")
        sys.exit()

    if mode == "truncate":
        result = bits[:TEST_LENGTH]

    elif mode == "substring":
        if start < 0 or start + TEST_LENGTH > len(bits):
            print(f"{CZERWONY}NIE{RESET} Nie można pobrać podciągu o wymaganej długości z podanej pozycji.")
            sys.exit()
        result = bits[start:start + TEST_LENGTH]

    print(f"{ZIELONY}TAK{RESET} Długość wejściowa: {len(bits)} bitów")
    print(f"{ZIELONY}TAK{RESET} Długość testowanego ciągu: {len(result)} bitów")

    return result


def load_bits_from_file(filename, mode="truncate", start=0):
    """Wczytuje ciąg binarny z pliku TXT i przygotowuje go do testów."""

    path = Path(filename)

    if not path.is_file():
        print(f"{CZERWONY}NIE{RESET} Nie znaleziono pliku: {filename}.")
        sys.exit()

    content = path.read_text(encoding="utf-8")

    # return prepare_bits(content, mode=mode, start=start)
    return content


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="bbs_test.py",
        description="Testy statystyczne FIPS 140-2",
        epilog="Projekt zaliczeniowy Podstawy kryptografii, Bartosz Grabski 59233 '2026"
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Plik TXT zawierający ciąg binarny 0/1"
    )

    parser.add_argument(
        "-s", "--start",
        type=int,
        default=0,
        help="Pozycja startowa od której testujemy ciąg z pliku"
    )

    parser.add_argument(
        "-c", "--count",
        type=int,
        default=20000,
        help="Liczba testowanych 0/1 (domyślnie: 20000)"
    )

    return parser.parse_args()

def monobit_test(bits):
    ones = bits.count("1")
    zeros = TEST_LENGTH - ones

    if DOPUSZCZALNA_LICZBA_JEDYNEK_MIN <= ones <= DOPUSZCZALNA_LICZBA_JEDYNEK_MAX:
        print(f"{ZIELONY}TAK{RESET} Test pojedynczych bitów")
    else:
        print(f"{CZERWONY}NIE{RESET} Test pojedynczych bitów")

    print(f"    Liczba jedynek: {ones}, minimum: {DOPUSZCZALNA_LICZBA_JEDYNEK_MIN}, maksimum: {DOPUSZCZALNA_LICZBA_JEDYNEK_MAX}")


def get_runs(bits):
    if not bits:
        return []

    runs = []
    current_bit = bits[0]
    length = 1

    for bit in bits[1:]:
        if bit == current_bit:
            length += 1
        else:
            runs.append((current_bit, length))
            current_bit = bit
            length = 1

    runs.append((current_bit, length))

    return runs


# ---------------------------------------------------------
# TEST 2: SERII (RUNS)
# ---------------------------------------------------------

def runs_test(bits):

    counts = {
        "0": [0] * 6,
        "1": [0] * 6
    }

    for bit, length in get_runs(bits):
        index = min(length, 6) - 1
        counts[bit][index] += 1

    details = {}
    passed = True

    for bit in ("0", "1"):
        for i, count in enumerate(counts[bit]):
            minimum, maximum = LIMITS[i]
            label = f"bit_{bit}_seria_{i + 1}{'+' if i == 5 else ''}"

            ok = minimum <= count <= maximum

            details[label] = {
                "liczba": count,
                "minimum": minimum,
                "maksimum": maximum,
                "zaliczony": ok
            }

            if not ok:
                passed = False

    if passed:
        print(f"{ZIELONY}TAK{RESET} Test serii")
    else:
        print(f"{CZERWONY}NIE{RESET} Test serii")

    print(f"    Długość serii 1 BIT 0: {details["bit_0_seria_1"]["liczba"]}, minimum: {details["bit_0_seria_1"]["minimum"]}, maksimum: {details["bit_0_seria_1"]["maksimum"]}")
    print(f"    Długość serii 1 BIT 1: {details["bit_1_seria_1"]["liczba"]}, minimum: {details["bit_1_seria_1"]["minimum"]}, maksimum: {details["bit_1_seria_1"]["maksimum"]}")
    print(f"    Długość serii 2 BIT 0: {details["bit_0_seria_2"]["liczba"]}, minimum: {details["bit_0_seria_2"]["minimum"]}, maksimum: {details["bit_0_seria_2"]["maksimum"]}")
    print(f"    Długość serii 2 BIT 1: {details["bit_1_seria_2"]["liczba"]}, minimum: {details["bit_1_seria_2"]["minimum"]}, maksimum: {details["bit_1_seria_2"]["maksimum"]}")
    print(f"    Długość serii 3 BIT 0: {details["bit_0_seria_3"]["liczba"]}, minimum: {details["bit_0_seria_3"]["minimum"]}, maksimum: {details["bit_0_seria_3"]["maksimum"]}")
    print(f"    Długość serii 3 BIT 1: {details["bit_1_seria_3"]["liczba"]}, minimum: {details["bit_1_seria_3"]["minimum"]}, maksimum: {details["bit_1_seria_3"]["maksimum"]}")
    print(f"    Długość serii 4 BIT 0: {details["bit_0_seria_4"]["liczba"]}, minimum: {details["bit_0_seria_4"]["minimum"]}, maksimum: {details["bit_0_seria_4"]["maksimum"]}")
    print(f"    Długość serii 4 BIT 1: {details["bit_1_seria_4"]["liczba"]}, minimum: {details["bit_1_seria_4"]["minimum"]}, maksimum: {details["bit_1_seria_4"]["maksimum"]}")
    print(f"    Długość serii 5 BIT 0: {details["bit_0_seria_5"]["liczba"]}, minimum: {details["bit_0_seria_5"]["minimum"]}, maksimum: {details["bit_0_seria_5"]["maksimum"]}")
    print(f"    Długość serii 5 BIT 1: {details["bit_1_seria_5"]["liczba"]}, minimum: {details["bit_1_seria_5"]["minimum"]}, maksimum: {details["bit_1_seria_5"]["maksimum"]}")
    print(f"    Długość serii 6+BIT 0: {details["bit_0_seria_6+"]["liczba"]}, minimum: {details["bit_0_seria_6+"]["minimum"]}, maksimum: {details["bit_0_seria_6+"]["maksimum"]}")
    print(f"    Długość serii 6+BIT 1: {details["bit_1_seria_6+"]["liczba"]}, minimum: {details["bit_1_seria_6+"]["minimum"]}, maksimum: {details["bit_1_seria_6+"]["maksimum"]}")


def long_run_test(bits):
    runs = get_runs(bits)

    longest = max(length for _, length in runs)

    long_runs = [
        {"bit": bit, "dlugosc": length}
        for bit, length in runs
        if length >= 26
    ]

    passed = len(long_runs) == 0

    if passed:
        print(f"{ZIELONY}TAK{RESET} Test długiej serii")
    else:
        print(f"{CZERWONY}NIE{RESET} Test długiej serii")

    print(f"    Najdłuższa seria: {longest}")

def poker_test(bits):
    frequencies = [0] * 16

    for i in range(0, TEST_LENGTH, 4):
        block = bits[i:i + 4]
        value = int(block, 2)
        frequencies[value] += 1

    x = (
        (16 / 5000) * sum(f ** 2 for f in frequencies)
        - 5000
    )

    passed = 2.16 < x < 46.17

    if passed:
        print(f"{ZIELONY}TAK{RESET} Test pokerowy")
    else:
        print(f"{CZERWONY}NIE{RESET} Test pokerowy")

    print(f"    Statystyka x: {x}, minimum: 2.16, maksimum: 46.17")

############################################

args = parse_arguments()

TEST_LENGTH = args.count

if args.input:
    bits = load_bits_from_file(args.input)
else:
    bits = load_bits_from_file("bbs_output.txt")

if args.start > 0:
    bits = prepare_bits(bits, mode="substring", start=args.start)
else:
    bits = prepare_bits(bits, mode="truncate", start=0)



validate_bits(bits)

monobit_test(bits)

runs_test(bits)

long_run_test(bits)

poker_test(bits)
