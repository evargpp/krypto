# SteganoPy – steganografia obrazów monochromatycznych

## 1. Opis projektu

SteganoPy jest aplikacją napisaną w języku Python, która umożliwia ukrywanie
wiadomości tekstowych w obrazach monochromatycznych (skala szarości).
Wykorzystuje metodę LSB (Least Significant Bit), czyli modyfikację
najmniej znaczącego bitu wartości jasności piksela.

Aplikacja udostępnia graficzny interfejs użytkownika oparty na Tkinter.

## 2. Wymagania

- Python 3.10 lub nowszy,
- Pillow,
- pytest (wyłącznie do uruchamiania testów).

Instalacja bibliotek:

```bash
python -m pip install -r requirements.txt
```

## 3. Uruchomienie aplikacji

W katalogu projektu wykonaj:

```bash
python main.py
```

## 4. Obsługa

1. Wybierz obraz wejściowy.
2. Wpisz wiadomość albo wczytaj ją z pliku TXT.
3. Wybierz opcję osadzania i wskaż miejsce zapisu obrazu wynikowego.
4. Aby odczytać wiadomość, wybierz obraz wynikowy i kliknij przycisk odczytu.

Obrazy są konwertowane do skali szarości. Wynik zapisywany jest jako PNG.

## 5. Opis algorytmu LSB

Obraz w skali szarości składa się z pikseli o wartościach od 0 do 255.
Każda wartość jest reprezentowana przez 8 bitów.

Przykładowo:

```text
Wartość piksela:  10110110
Bit wiadomości:          1
Wynik:            10110111
```

Zmianie ulega wyłącznie najmniej znaczący bit. Różnica jasności piksela
wynosi zatem najwyżej 1, co zwykle jest trudne do zauważenia.

W projekcie wykorzystywany jest jeden bit na piksel.

### Struktura wiadomości

W obrazie zapisywane są kolejno:

- 32 bity – długość wiadomości wyrażona w bajtach,
- właściwa wiadomość – bajty tekstu zakodowane w UTF-8.

Długość jest zapisana jako 4 bajty w kolejności big-endian.

### Kolejność zapisu

Piksele są przetwarzane wierszami: od lewej do prawej, a następnie od góry
do dołu. Ponieważ obraz jest monochromatyczny, każdy piksel przechowuje
dokładnie jeden bit.

## 6. Pojemność obrazu

Dla obrazu o szerokości W i wysokości H liczba pikseli wynosi:

```text
N = W * H
```

Pierwsze 32 piksele są przeznaczone na nagłówek. Pozostałe piksele
przechowują wiadomość.

Maksymalna pojemność w bajtach:

```text
pojemność = floor((W * H - 32) / 8)
```

Przykład dla obrazu 1000 × 800:

```text
N = 1000 * 800 = 800000 pikseli
pojemność = floor((800000 - 32) / 8)
pojemność = 99996 bajtów
```

## 7. Założenia i ograniczenia

- Obsługiwane formaty wejściowe: formaty odczytywane przez Pillow,
  w szczególności PNG i BMP.
- Obraz jest przetwarzany jako skala szarości (tryb L).
- Tekst jest kodowany w UTF-8.
- Wiadomość jest osadzana jawnie, bez szyfrowania.
- Maksymalna długość wiadomości zależy od rozmiaru obrazu.
- Wynik należy zapisywać w formacie bezstratnym PNG.
- Ponowna kompresja stratna, np. zapis do JPEG, może zniszczyć ukryte dane.
- Zmiana rozmiaru, filtracja lub edycja obrazu może uszkodzić wiadomość.
- Format nie zawiera podpisu ani sumy kontrolnej, dlatego przypadkowy obraz
  może zostać błędnie zinterpretowany jako nośnik wiadomości.

## 8. Testy

Testy uruchamia się poleceniem:

```bash
python -m pytest -v
```

Zestaw testów sprawdza:
- osadzanie i odczytywanie tekstu ASCII,
- obsługę polskich znaków UTF-8,
- obsługę pustej wiadomości,
- obliczanie pojemności,
- odrzucanie zbyt dużej wiadomości,
- konwersję obrazu RGB do skali szarości,
- brak modyfikacji obrazu źródłowego.

## 9. Wnioski

Metoda LSB pozwala ukryć tekst w obrazie monochromatycznym przy niewielkiej
zmianie wartości jasności pikseli. Wykorzystanie jednego bitu na piksel
zapewnia prostą implementację i ogranicza widoczne zniekształcenia.

Pojemność nośnika jest bezpośrednio zależna od liczby pikseli. Zastosowanie
nagłówka długości umożliwia jednoznaczne określenie liczby bajtów, które
należy odczytać. Format PNG jest istotny, ponieważ zachowuje wartości
pikseli bez strat.

Metoda LSB nie zapewnia poufności wiadomości. Osoba, która zna sposób
osadzania danych, może ją odczytać. Steganografia ukrywa fakt istnienia
wiadomości, ale nie zastępuje szyfrowania.

## 10. Struktura projektu

```text
SteganoPy_mono/
├── main.py
├── stegano.py
├── requirements.txt
├── README.md
└── tests/
    └── test_stegano.py
```
