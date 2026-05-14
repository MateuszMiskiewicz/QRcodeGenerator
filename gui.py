import tkinter as tk
from tkinter import messagebox


def start_app(on_generate_callback):
    root = tk.Tk()
    root.title("Generator QR")
    root.geometry("400x150")
    root.eval('tk::PlaceWindow . center')

    tk.Label(root, text="Wpisz tekst do zakodowania:", pady=10).pack()

    entry = tk.Entry(root, width=40)
    entry.pack(pady=5)
    entry.insert(0, "https://")
    entry.focus_set()

    def handle_click():
        text = entry.get()
        if not text:
            messagebox.showwarning("Błąd", "Pole nie może być puste!")
            return

        root.withdraw()
        on_generate_callback(text)
        root.destroy()

    btn = tk.Button(root, text="Generuj", command=handle_click, bg="#4CAF50", fg="white")
    btn.pack(pady=15)

    root.bind('<Return>', lambda e: handle_click())
    root.mainloop()
