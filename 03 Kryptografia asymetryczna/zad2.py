
import random
import hashlib


# ==================================================
# 1. Generowanie liczb pierwszych
# ==================================================

def is_prime(n):
    """Sprawdza, czy liczba jest pierwsza."""
    if n < 2:
        return False

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False

    return True


def generate_prime():
    """Generuje losową liczbę pierwszą."""
    while True:
        number = random.randint(1000, 9999)

        if is_prime(number):
            return number


# ==================================================
# 2. Funkcje pomocnicze RSA
# ==================================================

def gcd(a, b):
    """Oblicza największy wspólny dzielnik."""
    while b:
        a, b = b, a % b

    return a


def extended_gcd(a, b):
    """Rozszerzony algorytm Euklidesa."""
    if a == 0:
        return b, 0, 1

    g, x1, y1 = extended_gcd(b % a, a)

    x = y1 - (b // a) * x1
    y = x1

    return g, x, y


def mod_inverse(e, phi):
    """Oblicza odwrotność modularną."""
    g, x, _ = extended_gcd(e, phi)

    if g != 1:
        raise ValueError("Nie istnieje odwrotność modularna")

    return x % phi


# ==================================================
# 3. Generowanie pary kluczy RSA
# ==================================================

def generate_keys():
    p = generate_prime()
    q = generate_prime()

    while q == p:
        q = generate_prime()

    n = p * q
    phi = (p - 1) * (q - 1)

    # Wybór wykładnika publicznego
    e = 65537

    if e >= phi or gcd(e, phi) != 1:
        e = 3

        while gcd(e, phi) != 1:
            e += 2

    # Wyznaczenie wykładnika prywatnego
    d = mod_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key


# ==================================================
# 4. Podpisywanie wiadomości kluczem prywatnym
# ==================================================

def sign_message(message, private_key):
    d, n = private_key

    # Skrót wiadomości SHA-256
    digest = hashlib.sha256(message.encode("utf-8")).digest()

    # Zamiana skrótu na liczbę całkowitą
    message_hash = int.from_bytes(digest, byteorder="big")

    # Podpis RSA
    signature = pow(message_hash, d, n)

    return signature


# ==================================================
# 5. Weryfikacja podpisu kluczem publicznym
# ==================================================

def verify_signature(message, signature, public_key):
    e, n = public_key

    digest = hashlib.sha256(message.encode("utf-8")).digest()
    message_hash = int.from_bytes(digest, byteorder="big")

    verified_hash = pow(signature, e, n)

    return verified_hash == message_hash % n


# ==================================================
# 6. Główna część programu
# ==================================================

def main():

    # Wiadomość 20-znakowa
    message = "To jest test RSA '26"

    print("=" * 50)
    print("WIADOMOŚĆ")
    print("=" * 50)

    print("Treść:", message)
    print("Liczba znaków:", len(message))

    if len(message) != 20:
        raise ValueError("Wiadomość musi mieć dokładnie 20 znaków")

    # Generowanie pary kluczy A
    public_A, private_A = generate_keys()

    # Generowanie pary kluczy B
    public_B, private_B = generate_keys()

    print("\n" + "=" * 50)
    print("PARA KLUCZY A")
    print("=" * 50)

    print("Klucz publiczny A:", public_A)
    print("Klucz prywatny A:", private_A)

    print("\n" + "=" * 50)
    print("PARA KLUCZY B")
    print("=" * 50)

    print("Klucz publiczny B:", public_B)
    print("Klucz prywatny B:", private_B)

    # Podpisanie wiadomości przez A i B
    signature_A = sign_message(message, private_A)
    signature_B = sign_message(message, private_B)

    print("\n" + "=" * 50)
    print("PODPISYWANIE WIADOMOŚCI")
    print("=" * 50)

    print("Podpis A:", signature_A)
    print("Podpis B:", signature_B)

    # Weryfikacja podpisów
    verified_A = verify_signature(message, signature_A, public_A)
    verified_B = verify_signature(message, signature_B, public_B)

    print("\n" + "=" * 50)
    print("WERYFIKACJA WIADOMOŚCI")
    print("=" * 50)

    print("Weryfikacja podpisu A:", "POPRAWNA" if verified_A else "BŁĘDNA")
    print("Weryfikacja podpisu B:", "POPRAWNA" if verified_B else "BŁĘDNA")


if __name__ == "__main__":
    main()
