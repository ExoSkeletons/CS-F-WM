import sys
import webbrowser
from tkinter import ttk
from tkinter.font import Font
from typing import Callable, Any

from ui.app import WidgetFrame
from ui.scrollable_frame import ScrollableFrame


class TermsPage(WidgetFrame):
    on_accepted: Callable[[], Any] = lambda b: None

    def _create_widgets(self):
        with open('terms.txt', 'r', encoding='utf-8') as f:
            terms_text = f.read()

        # terms
        ttk.Label(self, text="Consent Form", font=Font(size=12, weight="bold")).pack()
        ttk.Label(self, text="Please read the form below carefully.", font=Font(size=8, slant="italic")).pack()
        online_doc_url = "https://arielacil-my.sharepoint.com/personal/harelb_ariel_ac_il/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fharelb%5Fariel%5Fac%5Fil%2FDocuments%2FParticipant%20Information%20and%20Consent%20Form%2Epdf&parent=%2Fpersonal%2Fharelb%5Fariel%5Fac%5Fil%2FDocuments&ga=1"
        ttk.Button(self, text="View Document Online", command=lambda: webbrowser.open(online_doc_url)).pack(anchor="e")

        # scroll text
        frame = ScrollableFrame(self, scroll_y=True, relief="sunken", padding=5)
        frame.pack(expand=True, fill='x')
        frame.canvas.config(width=600)
        text_content = ttk.Label(frame.content, text=terms_text, anchor="nw", justify="left")
        text_content.pack(expand=True, fill='x', padx=5, pady=5)

        def on_canvas_resize(event):
            text_content.configure(wraplength=event.width - 10)

        frame.canvas.bind("<Configure>", on_canvas_resize)

        # accept/reject buttons
        b_frame = ttk.Frame(self)
        b_frame.pack()
        ttk.Label(self, text="")
        ttk.Button(b_frame, text="Accept Terms and Continue", command=lambda: self.on_accepted()).grid(row=0, column=0)
        # ttk.Button(b_frame, text="Reject", command=lambda: sys.exit()).grid(row=0, column=1)


class AuthPage(WidgetFrame):
    on_login: Callable[[str], Any] = lambda uuid: None

    def _create_widgets(self):
        ttk.Label(self, text="Login:").pack()
        ttk.Label(self, text="TBI").pack()
        ttk.Button(self, text="Login", command=lambda: self.on_login("dummy")).pack()
