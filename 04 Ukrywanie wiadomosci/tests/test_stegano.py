"""Testy jednostkowe podstawowych funkcji modułu stegano.py."""

from pathlib import Path
from PIL import Image
import pytest

from stegano import (
    embed_message,
    extract_message,
    image_capacity_bytes,
    load_grayscale_image,
    SteganographyError,
)


def create_test_image(path, width=100, height=100, color=128):
    """Tworzy testowy obraz w skali szarości."""
    image = Image.new("L", (width, height), color)
    image.save(path, format="PNG")


def test_embed_and_extract_ascii(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    create_test_image(source)

    message = "Tajna wiadomosc 123"
    embed_message(source, output, message)

    assert extract_message(output) == message


def test_embed_and_extract_polish_characters(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    create_test_image(source)

    message = "Zażółć gęślą jaźń – test polskich znaków."
    embed_message(source, output, message)

    assert extract_message(output) == message


def test_empty_message(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    create_test_image(source)

    embed_message(source, output, "")
    assert extract_message(output) == ""


def test_capacity_calculation():
    image = Image.new("L", (100, 100))
    # 10000 pikseli - 32 bity nagłówka = 9968 bitów,
    # czyli 1246 pełnych bajtów.
    assert image_capacity_bytes(image) == 1246


def test_too_large_message_is_rejected(tmp_path):
    source = tmp_path / "small.png"
    output = tmp_path / "output.png"
    create_test_image(source, width=10, height=10)

    with pytest.raises(SteganographyError):
        embed_message(source, output, "To jest zdecydowanie za długa wiadomość")


def test_input_is_converted_to_grayscale(tmp_path):
    source = tmp_path / "rgb.png"
    Image.new("RGB", (100, 100), (100, 150, 200)).save(source)

    image = load_grayscale_image(source)
    assert image.mode == "L"


def test_source_image_is_not_modified(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    create_test_image(source)

    before = Image.open(source).tobytes()
    embed_message(source, output, "Test")
    after = Image.open(source).tobytes()

    assert before == after
