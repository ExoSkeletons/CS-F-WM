import threading
import webbrowser
from tkinter import PhotoImage
from tkinter.font import Font
from typing import Callable, Any

import ttkbootstrap as ttk

from config import config, data_dir_path, img_dir_path
from services.oauth2 import google_login
from ui.app import WidgetFrame, HeaderWidget
from ui.theme import Fonts, pad, padx, pady, pad_l
from ui.widgets.frame import ScrollableFrame
from ui.widgets.loading import Loader


class TermsPage(WidgetFrame):
    on_accepted: Callable[[], Any] = lambda b: None

    def _create_widgets(self):
        try:
            with open(data_dir_path + 'terms.txt', 'rt', encoding='utf-8') as f:
                terms_text = f.read()
        except OSError as e:
            print(e)
            input("Could not load terms.")
            exit(1)

        # terms
        ttk.Label(self, text="Consent Form", font=Fonts.h1).pack()
        ttk.Label(self, text="Please read the form below carefully.", font=Fonts.small).pack()
        online_doc_url = config["consent_form_url"]
        ttk.Button(
            self, text="View Document Online",
            bootstyle="link",
            command=lambda: webbrowser.open(online_doc_url)
        ).pack(anchor="e")

        # scroll text
        frame = ScrollableFrame(self, scroll_y=True, relief="sunken", padding=pad)
        frame.pack(expand=True, fill='x')
        frame.canvas.config(width=700, height=350)
        text_content = ttk.Label(frame.content, text=terms_text, anchor="nw", justify="left")
        text_content.pack(expand=True, fill='x', padx=padx, pady=pady)

        def on_canvas_resize(event):
            text_content.configure(wraplength=event.width - 10)

        frame.canvas.bind("<Configure>", on_canvas_resize)

        # accept/reject buttons
        b_frame = ttk.Frame(self)
        b_frame.pack(pady=pady)
        ttk.Label(self, text="")
        ttk.Button(
            b_frame, text="Accept Terms and Continue",
            bootstyle="success",
            command=lambda: self.on_accepted()
        ).grid(row=0, column=0, padx=padx)
        # ttk.Button(b_frame, text="Reject", command=lambda: sys.exit()).grid(row=0, column=1)


class AuthPage(WidgetFrame):
    user_id: str

    def _create_widgets(self):
        HeaderWidget(self.app, "logo.png", ['jct.png', 'ariel.png'], master=self).pack(pady=pad_l)
        ttk.Label(self, text="Welcome!", font=Fonts.h1).pack()
        ttk.Label(
            self,
            text="Thanks for participating in our Experiment.\nYou're contribution today helps us push Science forward!",
            font=Font(slant="italic"), justify="center",
        ).pack(pady=pady)
        ttk.Label(self, text="Please Login to continue", font=Fonts.h3).pack(pady=pady)
        self.g_img = PhotoImage(file=img_dir_path + "ic/" + "google.png")
        ttk.Button(
            self,
            compound="left", image=self.g_img, text="Log in with Google",
            bootstyle="success",
            command=lambda: self.login_async()
        ).pack(pady=pady)
        ttk.Button(self, text="Dummy Login", command=lambda: self.on_login("dummy", "test@example.com")).pack()
        self.load_spinner = Loader(self, bounce=True)

    def login_async(self):
        def worker():
            user = google_login()
            self.app.after(0, lambda: self.login_callback(user))

        threading.Thread(target=worker, daemon=True).start()
        self.load_spinner.pack()
        self.load_spinner.start()

    def on_login(self, uuid, email):
        pass

    def login_callback(self, user):
        self.app.raise_window()

        self.on_login(user['user_id'], user['email'])
