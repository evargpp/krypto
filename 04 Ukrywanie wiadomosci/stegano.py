"""
Moduł realizujący steganografię obrazu monochromatycznego metodą LSB.

W tym projekcie obraz monochromatyczny oznacza obraz w skali szarości
(Pillow mode "L"), w którym każdy piksel ma jedną wartość jasności z zakresu
0..255. Nie występują tu osobne kanały R, G i B.

W każdym pikselu wykorzystujemy wyłącznie najmniej znaczący bit (LSB).
Pozostałe siedem bitów wartości piksela pozostaje bez zmian.

Struktura danych zapisywanych w obrazie:
    [32-bitowa długość wiadomości w bajtach][wiadomość zakodowana jako UTF-8]

Nagłówek długości pozwala odczytać wiadomość bez stosowania znaku końca.
"""

from pathlib import Path
from PIL import Image


HEADER_SIZE_BITS = 32
BITS_PER_PIXEL = 1
MAX_MESSAGE_BYTES = (2**32) - 1


class SteganographyError(Exception):
    """Wyjątek zgłaszany w przypadku błędów operacji steganograficznych."""


def load_grayscale_image(image_path):
    """
    Otwiera obraz i konwertuje go do skali szarości.

    Konwersja do trybu "L" zapewnia jednolity sposób przetwarzania:
    każdy piksel jest pojedynczą liczbą 0..255.

    Zwracamy kopię obrazu, dzięki czemu plik źródłowy nie jest modyfikowany.
    """
    try:
        with Image.open(image_path) as source:
            return source.convert("L")
    except (OSError, ValueError) as exc:
        raise SteganographyError(
            f"Nie można otworzyć obrazu: {exc}"
        ) from exc


def image_capacity_bytes(image):
    """
    Oblicza maksymalną liczbę bajtów wiadomości możliwych do zapisania.

    Jeden piksel przechowuje jeden bit.
    Pierwsze 32 piksele są zarezerwowane na nagłówek, który przechowuje
    długość wiadomości w bajtach.

    Pojemność:
        (liczba_pikseli - 32) bitów / 8

    Wynik jest zaokrąglany w dół, ponieważ niepełny bajt nie może
    reprezentować kolejnego znaku/bajtu wiadomości.
    """
    total_pixels = image.width * image.height
    available_bits = total_pixels - HEADER_SIZE_BITS

    if available_bits < 0:
        return 0

    return available_bits // 8


def _bytes_to_bits(data):
    """
    Zamienia bajty na listę bitów.

    Kolejność jest najpierw od najbardziej znaczącego bitu (MSB)
    do najmniej znaczącego bitu każdego bajtu.

    Przykład:
        01000001 (litera A) -> [0, 1, 0, 0, 0, 0, 0, 1]
    """
    bits = []
    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def _bits_to_bytes(bits):
    """
    Składa listę bitów w bajty, czytając po osiem bitów.

    Funkcja zakłada, że liczba bitów jest wielokrotnością ośmiu.
    """
    if len(bits) % 8 != 0:
        raise SteganographyError("Liczba bitów nie jest wielokrotnością 8.")

    result = bytearray()

    for start in range(0, len(bits), 8):
        value = 0

        for bit in bits[start:start + 8]:
            value = (value << 1) | bit

        result.append(value)

    return bytes(result)


def _write_bit(pixel_value, bit):
    """
    Zapisuje jeden bit w najmniej znaczącym bicie wartości piksela.

    Operacja:
        nowa_wartość = (stara_wartość & 254) | bit

    Liczba 254 ma zapis binarny 11111110, więc wyzerowany zostaje
    wyłącznie najmniej znaczący bit. Następnie wstawiamy bit wiadomości.

    Maksymalna zmiana jasności pojedynczego piksela wynosi 1.
    """
    return (pixel_value & 0b11111110) | bit


def _read_bit(pixel_value):
    """Odczytuje najmniej znaczący bit wartości piksela."""
    return pixel_value & 1


def embed_message(input_image_path, output_image_path, message):
    """
    Osadza tekst w obrazie monochromatycznym.

    Argumenty:
        input_image_path  - ścieżka do obrazu źródłowego,
        output_image_path - ścieżka do zapisu obrazu wynikowego,
        message           - tekst, który ma zostać ukryty.

    Tekst jest kodowany do UTF-8. Dzięki temu możliwe jest poprawne
    przechowywanie polskich znaków, np. ą, ę, ł, ż.

    Funkcja zwraca słownik z podstawowymi informacjami o operacji.
    """
    if not isinstance(message, str):
        raise SteganographyError("Wiadomość musi być tekstem.")

    # Kodowanie tekstu do bajtów. Długość zapisujemy w bajtach,
    # a nie w znakach, ponieważ znaki UTF-8 mogą zajmować różną liczbę bajtów.
    message_bytes = message.encode("utf-8")

    if len(message_bytes) > MAX_MESSAGE_BYTES:
        raise SteganographyError("Wiadomość jest zbyt długa.")

    image = load_grayscale_image(input_image_path)
    capacity = image_capacity_bytes(image)

    if len(message_bytes) > capacity:
        raise SteganographyError(
            f"Wiadomość jest za duża. Jej rozmiar: {len(message_bytes)} B, "
            f"maksymalna pojemność obrazu: {capacity} B."
        )

    # Nagłówek to 4 bajty (32 bity), zapisane w kolejności big-endian.
    # Oznacza to, że najbardziej znaczący bajt występuje jako pierwszy.
    header = len(message_bytes).to_bytes(4, byteorder="big")

    # Łączymy nagłówek z właściwą wiadomością.
    payload = header + message_bytes

    # Zamieniamy całość na pojedyncze bity.
    payload_bits = _bytes_to_bits(payload)

    # getdata() zwraca piksele w kolejności wierszami:
    # od lewej do prawej, a następnie od góry do dołu.
    pixels = list(image.getdata())

    # Modyfikujemy tylko tyle pierwszych pikseli, ile potrzeba.
    for index, bit in enumerate(payload_bits):
        pixels[index] = _write_bit(pixels[index], bit)

    # Umieszczamy zmodyfikowane piksele w nowym obrazie.
    result = Image.new("L", image.size)
    result.putdata(pixels)

    # PNG jest formatem bezstratnym. Nie należy zapisywać wyniku jako JPEG,
    # ponieważ kompresja stratna mogłaby zmienić najmniej znaczące bity.
    try:
        result.save(output_image_path, format="PNG")
    except OSError as exc:
        raise SteganographyError(
            f"Nie można zapisać obrazu wynikowego: {exc}"
        ) from exc

    return {
        "message_bytes": len(message_bytes),
        "capacity_bytes": capacity,
        "used_pixels": len(payload_bits),
        "image_size": image.size,
    }


def extract_message(image_path):
    """
    Odczytuje wiadomość ukrytą w obrazie.

    Najpierw odczytywane są pierwsze 32 bity, z których odtwarzana jest
    długość wiadomości. Następnie odczytywana jest dokładnie taka liczba
    bajtów, jaka została zapisana w nagłówku.

    Jeżeli nagłówek wskazuje długość większą niż pojemność obrazu,
    zgłaszany jest błąd. Chroni to m.in. przed próbą odczytu obrazu,
    który nie zawiera poprawnej wiadomości w przyjętym formacie.
    """
    image = load_grayscale_image(image_path)
    pixels = list(image.getdata())

    if len(pixels) < HEADER_SIZE_BITS:
        raise SteganographyError(
            "Obraz jest zbyt mały, aby zawierać nagłówek wiadomości."
        )

    # Odczyt 32 bitów nagłówka.
    header_bits = [_read_bit(pixel) for pixel in pixels[:HEADER_SIZE_BITS]]
    header_bytes = _bits_to_bytes(header_bits)

    message_length = int.from_bytes(header_bytes, byteorder="big")

    capacity = image_capacity_bytes(image)

    if message_length > capacity:
        raise SteganographyError(
            "Nie znaleziono poprawnej wiadomości albo obraz został "
            "zmodyfikowany. Odczytana długość przekracza pojemność obrazu."
        )

    # Liczba bitów właściwej wiadomości.
    message_bits_count = message_length * 8

    # Wiadomość zaczyna się bezpośrednio za 32-bitowym nagłówkiem.
    start = HEADER_SIZE_BITS
    end = start + message_bits_count

    message_bits = [
        _read_bit(pixel)
        for pixel in pixels[start:end]
    ]

    message_bytes = _bits_to_bytes(message_bits)

    try:
        return message_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SteganographyError(
            "Odczytane dane nie są poprawnym tekstem UTF-8. "
            "Obraz może nie zawierać wiadomości zapisanej przez tę aplikację."
        ) from exc


def get_image_info(image_path):
    """Zwraca podstawowe informacje o obrazie i jego pojemności."""
    image = load_grayscale_image(image_path)

    return {
        "width": image.width,
        "height": image.height,
        "pixels": image.width * image.height,
        "capacity_bytes": image_capacity_bytes(image),
    }
