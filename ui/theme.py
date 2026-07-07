from tkinter import ttk


class Fonts:
    h1 = ("Segoe UI", 24, "bold")
    h2 = ("Segoe UI", 18, "bold")
    h3 = ("Segoe UI", 14, "bold")
    body = ("Segoe UI", 11)
    small = ("Segoe UI", 8, "italic")
    mono = ("Consolas", 10)


dim = {
    "maxw": 1080, "maxh": 820,
    "full": False,
}

pad = 15
pad_l = 50
padx, pady = 20, 20
padding = {'padx': padx, 'pady': pady}

sp = 10
spx, spy = 5, 5
spacing = {'padx': spx, 'pady': spy}


def configure_style():
    style = ttk.Style()

    def_font = Fonts.body

    style.configure(".", font=def_font)

    style.configure("TLabel", font=def_font)
    style.configure("TButton", font=def_font, padding=8)
    style.configure("TEntry", font=def_font)
