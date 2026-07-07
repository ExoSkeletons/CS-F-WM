import threading
import webbrowser
from tkinter.font import Font
from typing import Callable, Any

import ttkbootstrap as ttk

from config import config, data_dir_path
from services.oauth2 import google_login
from ui.app import WidgetFrame
from ui.scrollable_frame import ScrollableFrame
from ui.theme import Fonts, pad, padx, pady


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
        ttk.Label(self, text="Please read the form below carefully.", font=Font(size=8, slant="italic")).pack()
        online_doc_url = config["consent_form_url"]
        ttk.Button(
            self, text="View Document Online",
            bootstyle="info",
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
        b_frame.pack()
        ttk.Label(self, text="")
        ttk.Button(
            b_frame, text="Accept Terms and Continue",
            bootstyle="success",
            command=lambda: self.on_accepted()
        ).grid(row=0, column=0)
        # ttk.Button(b_frame, text="Reject", command=lambda: sys.exit()).grid(row=0, column=1)


class AuthPage(WidgetFrame):
    user_id: str

    def _create_widgets(self):
        ttk.Label(self, text="Welcome!", font=Font(size=22, weight="bold")).pack()
        ttk.Label(self, text="Please Login to continue:", font=Font(size=12, weight='bold')).pack()
        # ttk.Label(self, text="TBI").pack()
        ttk.Button(self, text="Log in with Google", command=lambda: self.login_async()).pack()
        ttk.Button(self, text="Dummy Login", command=lambda: self.on_login("dummy", "test@example.com")).pack()

    def login_async(self):
        def worker():
            user = google_login()
            self.app.after(0, lambda: self.login_callback(user))

        threading.Thread(target=worker, daemon=True).start()

    def on_login(self, uuid, email):
        pass

    def login_callback(self, user):
        self.app.raise_window()

        self.on_login(user['user_id'], user['email'])
