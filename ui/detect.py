import tkinter
from tkinter import END, font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Callable

from ui.app import App, WidgetFrame, rtl, config_enable_frame
from ui.scrollable_frame import ScrollableFrame


class DetectPage(WidgetFrame):
    on_submit: Optional[Callable[[str], None]] = None

    _font_size = 9
    _font_size_title = 18
    _min_word_count = 100

    _response_cell: Optional[str] = None

    def __init__(self, watermark: Callable[[str], str] | None, app: App, master: tkinter.Misc | None = None):
        self.mark = watermark

        super().__init__(app, master)

    def _create_widgets(self):
        # instructions
        ins_frame = ttk.Frame(self)
        wrap_l = 300
        ins_frame.grid(row=0, column=1, sticky="nwe")
        ttk.Label(
            ins_frame,
            text=rtl(
                "לפניכם שאלה לימודית.\nהשתמשו במודל שלפניכם וכתבו שאלה למודל - ארוכה ככל שתרצו, כדי לעזור לכם בפתרון השאלה."
            ),
            justify="right", anchor="ne", wraplength=wrap_l
        ).pack(expand=True, fill="both")
        ttk.Label(ins_frame, text=rtl("שאלה:")).pack()
        ttk.Label(
            ins_frame, text=rtl("< שאלה >"),
            font=font.Font(
                size=self._font_size_title,
                weight="bold", slant="italic"
            )
        ).pack()

        model_frame = ttk.Frame(self)
        model_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        # query label
        _user_font = font.Font(size=self._font_size, slant="italic")
        self.q_var: tkinter.StringVar = tkinter.StringVar()
        ttk.Label(model_frame, textvariable=self.q_var, font=_user_font).pack()

        # model response frame
        self.scroll = ScrollableFrame(model_frame, scroll_y=True)
        self.scroll.pack(fill="both", expand=True)
        self.text_var = tkinter.StringVar()
        self.t = ttk.Label(self.scroll.content, textvariable=self.text_var, anchor="n")
        self.bind("<Configure>", lambda event: self.t.configure(wraplength=event.width - 40))
        self.t.pack(anchor="center")

        # user response
        self.user_response_frame = ttk.Frame(ins_frame)
        user_reasoning_frame = ttk.Frame(self.user_response_frame)
        self.is_watermarked_var = tkinter.BooleanVar()
        (ttk.Label(
            self.user_response_frame,
            text=rtl("התבוננו בטקסט שלפניכם - האם לדעתכם מוסתר סימן מים בטקסט?"),
            justify="right", wraplength=wrap_l
        ).grid(row=0, column=0))
        # checkbox
        self.b = ttk.Checkbutton(self.user_response_frame, text="כן, יש סימן מים", variable=self.is_watermarked_var)
        self.b.grid(row=1, column=0)
        # reasoning
        reasoning = ttk.Label(user_reasoning_frame, text=rtl("כיצד זיהיתם את הסימן?"))
        user_reasoning_frame.grid(row=2, column=0, sticky="nsew")
        self.reasoning_var = tkinter.StringVar()
        reasoning.grid(row=0, column=1)
        reasoning_entry = ttk.Entry(user_reasoning_frame, textvariable=self.reasoning_var)
        reasoning_entry.grid(row=0, column=0, sticky="nsew")
        user_reasoning_frame.columnconfigure(0, weight=1)
        self.user_response_frame.columnconfigure(0, weight=1)
        # confirm
        answer_frame = ttk.Frame(self.user_response_frame)
        answer_frame.grid(row=3, column=0, columnspan=2)
        self._confirm_button = ttk.Button(answer_frame, text="Confirm Choice", command=lambda: self.submit_choices())
        self._confirm_button.grid(row=0, column=0)
        self.response_correctness_var = tkinter.StringVar()
        # results
        ttk.Label(answer_frame, textvariable=self.response_correctness_var).grid(row=0, column=1)

        self.is_watermarked_var.trace_add(
            "write",
            lambda var, index, mode: config_enable_frame(
                user_reasoning_frame,
                self.is_watermarked_var.get()
            )
        )
        self.user_response_frame.pack(fill="x", expand=True)
        self.is_watermarked_var.set(False)

        # query submission
        self.submit_frame = ttk.Frame(model_frame)
        self.submit_frame.pack(fill="x", expand=True)
        self._text_form = ScrolledText(self.submit_frame, height=1, width=1, wrap="word")
        self.app.set_on_submit(self._text_form, lambda: self.submit_query())
        self._text_form.grid(row=0, column=0, sticky="nswe")
        self.submit_frame.columnconfigure(0, weight=1)
        query_button = ttk.Button(self.submit_frame, text="שלח", command=lambda: self.submit_query())
        query_button.grid(row=0, column=1)
        self.app.set_on_submit(query_button, lambda: self.submit_query())

        self.app.set_focus_next(reasoning_entry, self._confirm_button)
        self.app.set_focus_next(self._text_form, self._confirm_button)

        super()._create_widgets()

        self.response(None)

    def submit_query(self):
        # get query
        q = self._text_form.get('1.0', END)
        if not q.strip(): return

        # set query label
        self.q_var.set(q)

        # clear responses
        self.response("Generating Response...", apply_marks=False)

        # disable query form
        config_enable_frame(self.submit_frame, False)

        # fire listener
        wrapped_q = q + "\n" + f"Your answer must be at least {self._min_word_count} words long."
        if self.on_submit: self.on_submit(wrapped_q)

    def response(self, response: str | None, apply_marks=True):
        # update model response text
        is_response = response is not None
        r = response if is_response else ""
        w = self.mark
        self.text_var.set(w(r) if w is not None and apply_marks else r)
        self.b.config(state="normal" if is_response and apply_marks else "disabled")
        self.is_watermarked_var.set(False)

        # update user response frame
        if is_response and apply_marks:
            self.user_response_frame.pack()
        else:
            self.user_response_frame.pack_forget()

        self._confirm_button.config(state="normal" if is_response and apply_marks else "disabled")
        self.response_correctness_var.set("")

        # scroll to frame top bottom
        self.scroll.update_idletasks()
        self.scroll.canvas.yview_moveto(0.0)

        # re-enable query form
        config_enable_frame(self.submit_frame, True)

        # clear query form
        self._text_form.delete('1.0', END)

    def submit_choices(self):
        # lock in choices
        config_enable_frame(self, False)

        # mark correct choices
        w = self.mark
        self.response_correctness_var.set(
            "Correct!" if ((w is not None) == self.is_watermarked_var.get())
            else "Incorrect"
        )
