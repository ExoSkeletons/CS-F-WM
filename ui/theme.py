from tkinter import ttk


FONTS = {
    "h1": ("Segoe UI", 24, "bold"),
    "h2": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10),
}

dim = {
    "maxw": 1080, "maxh": 820,
    "full": False,
}

pad = 10
pad_l = 50
padx, pady = 15, 15
padding = {'padx': padx, 'pady': pady}


def configure_style():
    style = ttk.Style()

    def_font = FONTS['body']

    style.configure(".", font=def_font)

    style.configure("TLabel", font=def_font)
    style.configure("TButton", font=def_font, padding=8)
    style.configure("TEntry", font=def_font)