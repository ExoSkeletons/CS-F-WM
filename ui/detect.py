import random
import threading
import tkinter
from tkinter import END, font
from tkinter import ttk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Callable

from ui.app import App, WidgetFrame, config_enable_frame, set_text
from ui.scrollable_frame import ScrollableFrame
from ui.survey import TimerFrame


class DetectPage(WidgetFrame):
    on_submit: Optional[Callable[[str], None]] = None

    _font_size = 12
    _font_size_title = 16
    _min_word_count = 100

    _response_cell: Optional[str] = None

    def __init__(
            self, app: App, master: tkinter.Misc | None = None,
            title: str = None,
            watermark: Callable[[str], str] | None = None, mark_prob: float = 1.0,
            questions=None
    ):
        # title
        self.title = title

        # random mark
        self.mark = random.choices([watermark, None], weights=[mark_prob, 1 - mark_prob])[0]

        # random question
        if questions is None:
            self.question_text = "< QUESTION >"
        else:
            self.question_text: str = random.choice(questions).strip().capitalize()

        super().__init__(app, master)

    def _create_widgets(self):
        # title
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=True, fill="x")
        ttk.Label(
            title_frame, text=self.title,
            font=Font(size=self._font_size, underline=True)
        ).pack(anchor="center")
        # timer frame
        self.timer = TimerFrame(title_frame)
        self.timer.pack(anchor="ne")
        self.timer.start()

        # body frame
        body = ttk.Frame(self)
        body.pack(expand=True, fill="both", anchor="center")

        # instructions
        ins_frame = ttk.Frame(body)
        ins_wrap_l = 300
        ins_col = 0
        ins_frame.grid(row=0, column=ins_col, sticky="nwe")
        self.question_frame = ttk.Frame(ins_frame)
        self.question_frame.pack(expand=True, fill="both")
        ttk.Label(
            self.question_frame,
            text=
            "You are given below a question from a school assignment, and an AI Assistant to your right."
            ,
            font=Font(size=self._font_size_title),
            justify="left", anchor="nw", wraplength=ins_wrap_l
        ).pack(expand=True, fill="both")
        ttk.Label(
            self.question_frame,
            text=
            "Use the AI Assistant given here for help with the assignment, by writing a single prompt question - as long as you'd like - to help you solve the question."
            ,
            font=Font(size=self._font_size),
            justify="left", anchor="nw", wraplength=ins_wrap_l
        ).pack(expand=True, fill="both")
        ttk.Label(self.question_frame, text="question:").pack()
        ttk.Label(
            self.question_frame, text=self.question_text,
            font=font.Font(
                size=self._font_size,
                weight="bold", slant="italic"
            ),
            wraplength=ins_wrap_l
        ).pack()

        # ai model frame
        model_frame = ttk.Frame(body, relief="sunken", padding=(5, 5))
        model_col = 1
        model_frame.grid(row=0, column=model_col, sticky="nsew")
        self.columnconfigure(model_col, weight=1)
        # title
        ttk.Label(model_frame, text="AI Model", font=Font(size=self._font_size_title)).pack()
        # query label
        _user_font = font.Font(size=self._font_size, slant="italic")
        self.q_var: tkinter.StringVar = tkinter.StringVar()
        ttk.Label(model_frame, textvariable=self.q_var, font=_user_font).pack()
        ttk.Label(model_frame, text="Response:").pack()
        # model response frame
        self.scroll = ScrollableFrame(model_frame, scroll_y=True, scroll_x=True)
        self.scroll.pack(fill="both", expand=True)
        self.text_var = tkinter.StringVar()
        # text form (editable)
        self.tt = tkinter.Text(self.scroll.content, wrap="word")
        self.text_var.trace_add("write", lambda var, index, mode: set_text(self.tt, self.text_var.get()))
        self.tt.grid(row=0, column=0, sticky="nsew")
        # text label (non-editable)
        self.tl = tkinter.Label(self.scroll.content, textvariable=self.text_var, anchor="nw", justify="left")
        self.tl.grid(row=0, column=0, sticky="nsew")
        self.tl.bind("<Configure>", lambda event: self.tl.configure(wraplength=event.width - 50))
        # query submission
        self.submit_frame = ttk.Frame(model_frame)
        self.submit_frame.pack(fill="x", expand=True)
        self._query_form = ScrolledText(self.submit_frame, height=1, width=1, wrap="word")
        self.app.set_on_submit(self._query_form, lambda: self.submit_query())
        self._query_form.grid(row=0, column=0, sticky="nswe")
        self.submit_frame.columnconfigure(0, weight=1)
        query_button = ttk.Button(self.submit_frame, text="Send", command=lambda: self.submit_query())
        query_button.grid(row=0, column=1)
        self.app.set_on_submit(query_button, lambda: self.submit_query())

        # user response
        self.user_response_frame = ttk.Frame(ins_frame)
        (ttk.Label(
            self.user_response_frame,
            text="Observe the response text you've received:",
            font=Font(size=self._font_size_title),
            justify="left", wraplength=ins_wrap_l
        ).grid(row=0, column=0, sticky="nw"))
        (ttk.Label(
            self.user_response_frame,
            text="Do you believe it has been watermarked? You may use any external resource.",
            justify="left", wraplength=ins_wrap_l
        ).grid(row=1, column=0, sticky="nw"))
        # yes/no radios
        self.is_wm_yes_var = tkinter.BooleanVar()
        self.is_wm_no_var = tkinter.BooleanVar()
        radio_frame = ttk.Frame(self.user_response_frame)
        self.b_wm_yes = ttk.Radiobutton(
            radio_frame, text="Yes",
            variable=self.is_wm_yes_var,
            command=lambda: self.is_wm_no_var.set(not self.is_wm_yes_var.get())
        )
        self.b_wm_no = ttk.Radiobutton(
            radio_frame, text="No",
            variable=self.is_wm_no_var,
            command=lambda: self.is_wm_yes_var.set(not self.is_wm_no_var.get())
        )
        self.b_wm_yes.grid(row=0, column=0)
        self.b_wm_no.grid(row=0, column=1)
        radio_frame.grid(row=2, column=0)
        # reasoning
        reasoning_frame = ttk.Frame(self.user_response_frame)
        reasoning_frame.grid(row=3, column=0, sticky="nsew")
        ttk.Label(
            reasoning_frame,
            text="What made you think text was watermarked?",
            justify="left", wraplength=ins_wrap_l
        ).pack(anchor="nw")
        entry_dim = (int(ins_wrap_l * 0.15), 3)
        tkinter.Text(
            reasoning_frame, wrap="word",
            width=entry_dim[0], height=entry_dim[1],
        ).pack(expand=True)
        ttk.Label(
            reasoning_frame,
            text="If so, try to remove it by editing the text response.\nDo you best to remove only the watermark and keep the original text intact as much as possible.",
            font=Font(size=self._font_size, slant="italic"),
            justify="left", wraplength=ins_wrap_l
        ).pack(anchor="nw")
        ttk.Label(
            reasoning_frame,
            text="What did you do to try and remove the watermark?",
            justify="left", wraplength=ins_wrap_l
        ).pack(anchor="nw")
        tkinter.Text(
            reasoning_frame, wrap="word",
            width=entry_dim[0], height=entry_dim[1],
        ).pack(expand=True)
        self.user_response_frame.columnconfigure(1, weight=1)
        # confirm
        answer_frame = ttk.Frame(self.user_response_frame)
        answer_frame.grid(row=4, column=0, columnspan=2)
        confirm_button = ttk.Button(answer_frame, text="Confirm Choice", command=lambda: self.confirm_choices())
        # confirm_button.grid(row=0, column=0)
        self._response_correctness_var = tkinter.StringVar()
        # results
        ttk.Label(answer_frame, textvariable=self._response_correctness_var).grid(row=0, column=1)

        def update_user_response(is_w: bool = False):
            self.set_text_editable(is_w)
            config_enable_frame(reasoning_frame, is_w)
            self.event_generate("<<PageValidityChanged>>")

        self.is_wm_yes_var.trace_add(
            "write",
            lambda var, index, mode: update_user_response(self.is_wm_yes_var.get())
        )
        self.user_response_frame.pack(fill="x", expand=True)

        # self.app.set_focus_next(reasoning_entry, remove_entry)
        # self.app.set_focus_next(remove_entry, confirm_button)
        # self.app.set_focus_next(self._query_form, confirm_button)

        super()._create_widgets()

        self.set_response_text("Hi! How can I help you today?")

    def submit_query(self):
        # get query
        q = self._query_form.get('1.0', END)
        if not q.strip(): return

        # set query label
        self.q_var.set(q)

        # clear responses
        self.set_response_text("Generating Response...")

        # disable query form
        config_enable_frame(self.submit_frame, False)

        # fire listener
        wrapped_q = (
                q + "\n" +
                f"Your answer must be at least {self._min_word_count} words long." +
                "Your answer must be entirely plaintext and contain NO highlights or formatting (no bold, italic or any markdown)."
        )
        if self.on_submit: self.on_submit(wrapped_q)

    def set_text_editable(self, enabled: bool = True):
        if enabled:
            self.tl.lower()
            self.tt.lift()
        else:
            self.tl.lift()
            self.tt.lower()

    def set_response_text(self, text: str | None, user_response_enabled: bool = False):
        # update user instructions
        if user_response_enabled:
            self.question_frame.pack_forget()
            self.user_response_frame.pack()
        else:
            self.question_frame.pack()
            self.user_response_frame.pack_forget()

        # set text
        self.text_var.set(text)

        # scroll to frame top bottom
        self.scroll.update_idletasks()
        self.scroll.canvas.yview_moveto(0.0)

        # re-enable query form
        if user_response_enabled:
            self.submit_frame.pack_forget()
        else:
            self.submit_frame.pack()

        # clear query form
        self._query_form.delete('1.0', END)

    def response(self, response: str | None, ok: bool = True):
        # update model response text
        if response is None or not ok:
            self.app.after(0, lambda: self.set_response_text(response))
            return

        def watermark_worker():
            wm = self.mark
            wmr = wm(response) if wm is not None else response

            self.is_wm_yes_var.set(False)
            self.is_wm_no_var.set(False)
            self._response_correctness_var.set("")

            # update UI safely from main thread
            self.app.after(0, lambda: self.set_response_text(wmr, user_response_enabled=True))

        self.set_response_text("Watermarking...")

        threading.Thread(target=watermark_worker, daemon=True).start()

    def confirm_choices(self):
        # lock in choices
        config_enable_frame(self, False)
        self.set_text_editable(False)

        # mark correct choices
        w = self.mark
        self._response_correctness_var.set(
            "Correct!" if ((w is not None) == self.is_wm_yes_var.get())
            else "Incorrect"
        )

        # stop timer
        self.timer.stop()

    def is_valid(self) -> bool:
        if self.is_wm_yes_var.get() == self.is_wm_no_var.get():
            # todo: show "red" required-notice and return False if not.
            return False
        return True
