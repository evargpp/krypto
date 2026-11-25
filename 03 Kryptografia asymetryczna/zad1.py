import random
import math

def generate_prime():
    while True:
        number = random.randint(1000, 9999)

        if number > 1 and all(
            number % i != 0
            for i in range(2, math.isqrt(number) + 1)
        ):
            return number

def generate_keys():
    p = generate_prime()
    q = generate_prime()

    while p == q:
        q = generate_prime()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537

    while math.gcd(e, phi) != 1:
        e += 2

    d = pow(e, -1, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key

def generate_message():
    message = "To jest przykladowa wiadomosc do testowania RSA123"
    return message[:50].ljust(50)

def encrypt(message, public_key):
    e, n = public_key

    encrypted = []

    for char in message:
        m = ord(char)
        c = pow(m, e, n)
        encrypted.append(c)

    return encrypted

def decrypt(encrypted, private_key):
    d, n = private_key

    decrypted = ""

    for char in encrypted:
        m = pow(char, d, n)
        decrypted += chr(m)

    return decrypted

def main():
    public_key, private_key = generate_keys()

    message = generate_message()

    encrypted = encrypt(message, public_key)

    decrypted = decrypt(encrypted, private_key)

    print("Wiadomość oryginalna:")
    print(message)

    print("\nKlucz publiczny:")
    print(public_key)

    print("\nKlucz prywatny:")
    print(private_key)

    print("\nWiadomość zaszyfrowana:")
    print(encrypted)

    print("\nWiadomość odszyfrowana:")
    print(decrypted)

    print("\nPorównanie wiadomości:")
    print("POPRAWNA" if message == decrypted else "NIEPOPRAWNA")


if __name__ == "__main__":
    main()