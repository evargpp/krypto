"""
SteganoPy – graficzna aplikacja do ukrywania tekstu w obrazach
monochromatycznych (skala szarości) metodą LSB.

Uruchomienie:
    python main.py

Wymagana biblioteka:
    Pillow
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from stegano import (
    embed_message,
    extract_message,
    get_image_info,
    SteganographyError,
)


class SteganoPyApp:
    """Główna klasa interfejsu graficznego aplikacji."""

    def __init__(self, root):
        self.root = root
        self.root.title("SteganoPy – steganografia LSB")
        self.root.geometry("720x570")
        self.root.minsize(620, 500)

        # Ścieżka do aktualnie wybranego obrazu.
        self.selected_image = None

        self._build_interface()

    def _build_interface(self):
        """Tworzy wszystkie elementy okna aplikacji."""

        title = tk.Label(
            self.root,
            text="SteganoPy",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(15, 2))

        subtitle = tk.Label(
            self.root,
            text="Ukrywanie wiadomości w obrazach monochromatycznych – LSB",
            font=("Arial", 10)
        )
        subtitle.pack(pady=(0, 12))

        # Sekcja wyboru obrazu.
        image_frame = tk.LabelFrame(
            self.root,
            text="Obraz monochromatyczny",
            padx=10,
            pady=10
        )
        image_frame.pack(fill="x", padx=15, pady=5)

        self.image_label = tk.Label(
            image_frame,
            text="Nie wybrano obrazu",
            anchor="w"
        )
        self.image_label.pack(fill="x", pady=3)

        tk.Button(
            image_frame,
            text="Wybierz obraz",
            command=self.choose_image
        ).pack(anchor="w", pady=4)

        self.info_label = tk.Label(
            image_frame,
            text="Pojemność obrazu: —",
            anchor="w"
        )
        self.info_label.pack(fill="x", pady=3)

        # Sekcja osadzania wiadomości.
        embed_frame = tk.LabelFrame(
            self.root,
            text="Osadzanie wiadomości",
            padx=10,
            pady=10
        )
        embed_frame.pack(fill="both", expand=True, padx=15, pady=5)

        tk.Label(
            embed_frame,
            text="Wpisz tekst, który ma zostać ukryty:"
        ).pack(anchor="w")

        self.message_text = tk.Text(
            embed_frame,
            height=7,
            wrap="word"
        )
        self.message_text.pack(fill="both", expand=True, pady=5)

        buttons_frame = tk.Frame(embed_frame)
        buttons_frame.pack(fill="x", pady=4)

        tk.Button(
            buttons_frame,
            text="Wczytaj tekst z pliku",
            command=self.load_text_file
        ).pack(side="left")

        tk.Button(
            buttons_frame,
            text="Osadź i zapisz obraz",
            command=self.embed
        ).pack(side="right")

        # Sekcja odczytywania wiadomości.
        extract_frame = tk.LabelFrame(
            self.root,
            text="Odczytywanie wiadomości",
            padx=10,
            pady=10
        )
        extract_frame.pack(fill="x", padx=15, pady=5)

        tk.Button(
            extract_frame,
            text="Odczytaj wiadomość z wybranego obrazu",
            command=self.extract
        ).pack(anchor="w")

        # Pole prezentujące odczytaną wiadomość.
        self.extracted_text = tk.Text(
            extract_frame,
            height=5,
            wrap="word",
            state="disabled"
        )
        self.extracted_text.pack(fill="x", pady=(7, 0))

        # Pasek statusu.
        self.status_label = tk.Label(
            self.root,
            text="Gotowy do pracy.",
            anchor="w",
            relief="sunken"
        )
        self.status_label.pack(fill="x", side="bottom")

    def choose_image(self):
        """Otwiera okno dialogowe wyboru obrazu."""
        path = filedialog.askopenfilename(
            title="Wybierz obraz",
            filetypes=[
                ("Obrazy PNG i BMP", "*.png *.bmp"),
                ("Wszystkie pliki", "*.*"),
            ],
        )

        if not path:
            return

        try:
            info = get_image_info(path)
        except SteganographyError as exc:
            messagebox.showerror("Błąd obrazu", str(exc))
            return

        self.selected_image = path
        self.image_label.config(text=Path(path).name)
        self.info_label.config(
            text=(
                f"Wymiary: {info['width']} × {info['height']} px | "
                f"Liczba pikseli: {info['pixels']} | "
                f"Maksymalna wiadomość: {info['capacity_bytes']} B"
            )
        )
        self.status_label.config(text="Wybrano obraz.")

    def load_text_file(self):
        """Wczytuje treść wiadomości z pliku tekstowego UTF-8."""
        path = filedialog.askopenfilename(
            title="Wybierz plik tekstowy",
            filetypes=[
                ("Pliki tekstowe", "*.txt"),
                ("Wszystkie pliki", "*.*"),
            ],
        )

        if not path:
            return

        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            messagebox.showerror(
                "Błąd odczytu pliku",
                f"Nie udało się odczytać pliku:\n{exc}"
            )
            return

        self.message_text.delete("1.0", tk.END)
        self.message_text.insert("1.0", text)
        self.status_label.config(text="Wczytano wiadomość z pliku.")

    def embed(self):
        """Osadza wpisaną wiadomość i zapisuje wynikowy obraz PNG."""
        if not self.selected_image:
            messagebox.showwarning(
                "Brak obrazu",
                "Najpierw wybierz obraz wejściowy."
            )
            return

        message = self.message_text.get("1.0", "end-1c")

        if not message:
            messagebox.showwarning(
                "Brak wiadomości",
                "Wpisz wiadomość, którą chcesz ukryć."
            )
            return

        output_path = filedialog.asksaveasfilename(
            title="Zapisz obraz z ukrytą wiadomością",
            defaultextension=".png",
            filetypes=[("Obraz PNG", "*.png")],
            initialfile="obraz_z_wiadomoscia.png",
        )

        if not output_path:
            return

        try:
            result = embed_message(
                self.selected_image,
                output_path,
                message
            )
        except SteganographyError as exc:
            messagebox.showerror("Nie udało się osadzić wiadomości", str(exc))
            return

        messagebox.showinfo(
            "Sukces",
            "Wiadomość została osadzona.\n\n"
            f"Rozmiar wiadomości: {result['message_bytes']} B\n"
            f"Pojemność obrazu: {result['capacity_bytes']} B\n"
            f"Zapisany plik: {output_path}"
        )
        self.status_label.config(text="Wiadomość została osadzona.")

    def extract(self):
        """Odczytuje wiadomość z aktualnie wybranego obrazu."""
        if not self.selected_image:
            messagebox.showwarning(
                "Brak obrazu",
                "Najpierw wybierz obraz, z którego chcesz odczytać wiadomość."
            )
            return

        try:
            message = extract_message(self.selected_image)
        except SteganographyError as exc:
            messagebox.showerror("Błąd odczytu", str(exc))
            return

        self.extracted_text.config(state="normal")
        self.extracted_text.delete("1.0", tk.END)
        self.extracted_text.insert("1.0", message)
        self.extracted_text.config(state="disabled")

        self.status_label.config(text="Odczytano wiadomość.")


def main():
    """Punkt wejścia programu."""
    root = tk.Tk()
    SteganoPyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
