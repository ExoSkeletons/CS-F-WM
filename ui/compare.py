import random
import tkinter
from tkinter import END, font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Callable, List

from ui.app import AppPage, App
from ui.scrollable_frame import ScrollableFrame


class ComparePage(AppPage):
    on_submit: Optional[Callable[[str], None]] = None

    _font_size = 9

    class ResponseFrame(ttk.Frame):
        def __init__(self, master: tkinter.Misc | None):
            super().__init__(master)

            self.text_var = tkinter.StringVar()
            self.l = ttk.Label(self, textvariable=self.text_var, anchor="n")
            self.l.grid(row=0, sticky="nswe")
            self.rowconfigure(0, weight=1)
            self.selected = tkinter.BooleanVar()
            b = ttk.Checkbutton(self, text="Watermarked?", variable=self.selected)
            b.grid(row=1)

            # Dynamically adjust wrap length when resized
            self.bind("<Configure>", self._on_resize)

        def _on_resize(self, event):
            # Set wrap length to current width minus padding
            self.l.configure(wraplength=event.width - 10)

    _response_cell: Optional[str] = None

    responses: List[ResponseFrame] = []

    def __init__(self, app: App, watermarks: List[Callable[[str], str]]):
        super().__init__(app)
        self.marks: List[Callable[[str], str] | None] = list(watermarks)
        self.marks.append(None)
        random.shuffle(self.marks)

    def _create_widgets(self):
        self.scroll = ScrollableFrame(self, scroll_y=True)
        self.scroll.pack(fill="both", expand=True)

        fp = ttk.Frame(self.scroll.content)
        for i, w in enumerate(self.marks):
            self.responses.append(ComparePage.ResponseFrame(fp))
            # self.responses[i].text_var.set(f"TEXT VAR {i}")
            self.responses[i].grid(row=0, column=i, sticky="nsew", padx=10 if i < len(self.marks) - 1 else 0)
            fp.columnconfigure(i, weight=1)
        fp.pack(fill="both", expand=True)

        # query label
        _user_font = font.Font(size=self._font_size, slant="italic")
        self.qvar: tkinter.StringVar = tkinter.StringVar()
        ttk.Label(
            self,
            textvariable=self.qvar, font=_user_font,
        ).pack()


        submit_frame = ttk.Frame(self)
        submit_frame.pack(fill="x")

        self._text_form = ScrolledText(submit_frame, height=1, wrap="word")
        self.app.set_on_submit(self._text_form, lambda: self.submit())
        self._text_form.grid(row=0,column=0, sticky="nswe")
        submit_frame.columnconfigure(0, weight=1)

        self._submit_button = ttk.Button(submit_frame, text="Generate", command=lambda: self.submit())
        self._submit_button.grid(row=0,column=1)
        self.app.set_on_submit(self._submit_button, lambda: self.submit())

        super()._create_widgets()

    def submit(self):
        # get query
        q = self._text_form.get('1.0', END)
        if not q.strip(): return

        # set query label
        self.qvar.set(q)

        # disable query form
        self._text_form.config(state="disabled")
        self._submit_button.config(state="disabled")

        # clear responses
        self.response("Generating...", apply_marks=False)

        # fire listener
        if self.on_submit: self.on_submit(q)

    def response(self, response: str | None, apply_marks=True):
        # update responses
        _response_font = font.Font(size=self._font_size)
        r = response if response is not None else ""
        for i, w in enumerate(self.marks):
            self.responses[i].text_var.set(w(r) if w is not None and apply_marks else r)

        # scroll to frame top bottom
        self.scroll.update_idletasks()
        self.scroll.canvas.yview_moveto(0.0)

        # re-enable query form
        self._text_form.config(state="normal")
        self._submit_button.config(state="normal")
        # clear query form
        self._text_form.delete('1.0', END)
