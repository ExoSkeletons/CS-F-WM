import random
import threading
from datetime import datetime, timedelta
from tkinter import END, StringVar, Misc
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Callable

import ttkbootstrap as ttk

from config import config
from ui.app import App, WidgetFrame, config_enable, set_text, config_style_as_label, WrappingLabel
from ui.scrollable_frame import ScrollableFrame
from ui.survey import TimerFrame, DataCollector
from ui.theme import padx, pady, Fonts
from watermark.types import Watermark


class DetectPage(WidgetFrame, DataCollector):
    on_submit: Optional[Callable[[str], None]] = None

    _min_word_count = 100
    _min_response_char_count = 30

    entry_w, entry_h = 30, 3

    _response_cell: Optional[str] = None

    _timers_q_t0 = datetime.now()
    _timers_gen_d: Optional[timedelta] = None
    _timers_wm_t0 = datetime.now()
    _timers_wm_d: Optional[timedelta] = None
    _timers_wm0 = datetime.now()

    mark: Optional[Watermark]
    mr: StringVar
    wmr: StringVar

    def __init__(
            self, app: App, master: Optional[Misc] = None,
            title: str = None,
            watermark: Optional[Watermark] = None, mark_prob: float = 1.0,
            questions=None
    ):
        # title
        self.title = title

        # random mark
        self.mark = random.choices(
            [watermark, None],
            weights=[mark_prob, 1 - mark_prob]
        )[0]

        # random question
        self.question_text = ''
        if questions is None:
            self.question_text = "< QUESTION >"
        else:
            self.question_text = random.choice(questions).strip().capitalize()

        super().__init__(app, master)

    def _create_widgets(self):
        # todo: split to widgets
        # title
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=True, fill="x")
        ttk.Label(
            title_frame, text=self.title,
            font=Font(font=Fonts.h1, underline=True)
        ).grid(row=0, column=0, sticky="nsw")
        title_frame.columnconfigure(0, weight=1)
        # timer frame
        self.timer = TimerFrame(title_frame)
        self.timer.grid(row=0, column=1, sticky="nse")
        self.timer.start()

        # body frame
        body_frame = ttk.Frame(self)
        body_frame.pack(expand=True, fill="both", anchor="center")
        body_frame.rowconfigure(0, weight=1)

        ins_col, model_col = 0, 1
        body_frame.columnconfigure(ins_col, weight=1)
        body_frame.columnconfigure(model_col, weight=3)

        # instructions
        ins_frame = ttk.Frame(body_frame)
        ins_frame.grid(row=0, column=ins_col, sticky="nwe")
        self.question_frame = ttk.Frame(ins_frame)
        self.question_frame.pack(expand=True, fill="both")
        WrappingLabel(
            self.question_frame,
            text=
            "You are given below a question from a school assignment, and an AI Assistant to your right."
            ,
            font=Fonts.h2,
            justify="left", anchor="nw",
        ).pack(expand=True, fill="both")
        WrappingLabel(
            self.question_frame,
            text=
            "Use the AI Assistant given here for help with the assignment, by writing a single prompt question - as long as you'd like - to help you solve the question."
            ,
            font=Fonts.small,
            justify="left", anchor="nw",
        ).pack(expand=True, fill="both")
        # question
        ttk.Label(self.question_frame, font=Fonts.small, text="question:").pack()
        q_label = ttk.Text(
            self.question_frame,
            font=Fonts.h3,
            wrap='word', width=self.entry_w, height=4
        )
        config_style_as_label(q_label, self.app)
        set_text(q_label, self.question_text)
        config_enable(q_label, False)
        q_label.pack(expand=True, fill="x")

        # model vars
        self.mr = StringVar(value=None)
        self.wmr = StringVar(value=None)
        # ai model frame
        model_frame = ttk.Frame(body_frame, relief="sunken", padding=(padx, pady))
        model_frame.grid(row=0, column=model_col, sticky="nsew")
        model_header = ttk.Frame(model_frame)
        model_header.pack(fill='x', expand=True)

        self._img_model = ttk.PhotoImage(file="ui/imgs/" + "model.png")
        ttk.Label(
            model_header,
            image=self._img_model
        ).grid(row=0, column=0)
        model_info = ttk.Frame(model_header)
        model_info.grid(row=0, column=1, sticky="nsw")
        model_header.columnconfigure(1, weight=1)

        # title
        ttk.Label(model_info, text="AI Assistant", font=Fonts.h2).pack()
        # query label
        self.q_var: ttk.StringVar = ttk.StringVar()
        WrappingLabel(model_info, textvariable=self.q_var, font=Fonts.small).pack()

        model_body = ttk.Frame(model_frame)
        model_body.pack(fill='x', expand=True)
        # ttk.Label(model_body, text="Response:").pack()
        # model response frame
        self.scroll = ScrollableFrame(model_body, scroll_y=True, scroll_x=True)
        self.scroll.pack(fill="both", expand=True)
        self.text_var = ttk.StringVar()
        response_font = Font(font=Fonts.body, size=10)
        # text form (editable)
        self.tt = ttk.Text(self.scroll.content, wrap="word", font=response_font)
        self.text_var.trace_add("write", lambda var, index, mode: set_text(self.tt, self.text_var.get()))
        self.tt.grid(row=0, column=0, sticky="nsew")
        # text label (non-editable)
        # self.tl = tkinter.Label(self.scroll.content, textvariable=self.text_var, anchor="nw", justify="left")
        self.tl = ttk.Text(self.scroll.content, wrap="word", font=response_font)
        config_style_as_label(self.tl, self.app)
        config_enable(self.tl, False)
        self.text_var.trace_add("write", lambda var, index, mode: set_text(self.tl, self.text_var.get(), force=True))
        self.tl.grid(row=0, column=0, sticky="nsew")
        # self.tl.bind("<Configure>", lambda event: self.tl.configure(wraplength=event.width - 50))
        # query submission
        self.submit_frame = ttk.Frame(model_body)
        self.submit_frame.pack(fill="x", expand=True)
        self._query_form = ScrolledText(self.submit_frame, height=1, width=1, wrap="word")
        self.app.set_on_submit(self._query_form, lambda: self.submit_query())
        self._query_form.grid(row=0, column=0, sticky="nswe")
        self.submit_frame.columnconfigure(0, weight=1)
        self._img_submit = ttk.PhotoImage(file="ui/imgs/ic/" + "send.png")
        query_button = ttk.Button(
            self.submit_frame,
            compound="right", image=self._img_submit,
            # text="Send",
            bootstyle="info",
            command=lambda: self.submit_query()
        )
        query_button.grid(row=0, column=1)
        self.app.set_on_submit(query_button, lambda: self.submit_query())

        # user response
        self.user_response_frame = ttk.Frame(ins_frame)
        (WrappingLabel(
            self.user_response_frame,
            text="Observe the response text you've received:",
            font=Fonts.h2,
            justify="left",
        ).grid(row=0, column=0, sticky="nw"))
        (WrappingLabel(
            self.user_response_frame,
            text="• Do you believe it has been watermarked? You may use any external resource.",
            justify="left"
        ).grid(row=1, column=0, sticky="nw"))
        # yes/no radios
        self.is_wm_yes_var = ttk.BooleanVar()
        self.is_wm_no_var = ttk.BooleanVar()
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
        self.is_wm_yes_var.trace_add("write", lambda v, i, m: self.validity_changed())
        self.is_wm_no_var.trace_add("write", lambda v, i, m: self.validity_changed())
        radio_frame.grid(row=2, column=0)
        # reasoning
        reasoning_frame = ttk.Frame(self.user_response_frame)
        reasoning_frame.grid(row=3, column=0, sticky="nsew")
        reasoning_detect_frame = ttk.Frame(reasoning_frame)
        reasoning_detect_frame.pack()
        WrappingLabel(
            reasoning_detect_frame,
            text="• What made you think text was watermarked?",
            justify="left"
        ).pack(anchor="nw")
        self.reasoning_detect_entry = ttk.Text(
            reasoning_detect_frame,
            wrap="word", undo=True, maxundo=10,
            width=self.entry_w, height=self.entry_h,
        )
        self.reasoning_detect_entry.pack(expand=True, fill="x")
        len_rd_frame = ttk.Frame(reasoning_detect_frame)
        len_rd_frame.pack(expand=True, fill="x")
        ttk.Label(
            len_rd_frame,
            text=f"Your response must be at least {self._min_response_char_count} characters long.",
            bootstyle="secondary",
            font=Font(size=7, slant='italic')
        ).grid(row=0, column=0, sticky="nsw")
        len_rd_frame.columnconfigure(0, weight=1)
        rd_len_l = ttk.Label(len_rd_frame)
        rd_len_l.grid(row=0, column=1)
        self.len_rd_var = ttk.IntVar()
        self.len_rd_var.trace_add("write", lambda m, l, c: rd_len_l.config(
            text=f"{self.len_rd_var.get()}/{self._min_response_char_count}"
        ))
        reasoning_change_frame = ttk.Frame(reasoning_frame)
        reasoning_change_frame.pack()
        WrappingLabel(
            reasoning_change_frame,
            text="• If so, try to remove it by editing the text response.\nDo your best to remove only the watermark and keep the original text intact as much as possible.",
            justify="left"
        ).pack(anchor="nw")
        WrappingLabel(
            reasoning_change_frame,
            text="• What did you do to try and remove the watermark?",
            justify="left"
        ).pack(anchor="nw")
        self.reasoning_change_entry = ttk.Text(
            reasoning_change_frame,
            wrap="word", undo=True, maxundo=10,
            width=self.entry_w, height=self.entry_h,
        )
        self.reasoning_change_entry.pack(expand=True, fill="x")
        len_rc_frame = ttk.Frame(reasoning_change_frame)
        len_rc_frame.pack(expand=True, fill="x")
        WrappingLabel(
            len_rc_frame,
            text=f"Your response must be at least {self._min_response_char_count} characters long.",
            bootstyle="secondary",
            anchor='nw', font=Font(size=7, slant='italic')
        ).grid(row=0, column=0, sticky="nsw")
        len_rc_frame.columnconfigure(0, weight=1)
        rc_len_l = ttk.Label(len_rc_frame)
        rc_len_l.grid(row=0, column=1)
        self.len_rc_var = ttk.IntVar()
        self.len_rc_var.trace_add("write", lambda m, l, c: rc_len_l.config(
            text=f"{self.len_rc_var.get()}/{self._min_response_char_count}"
        ))
        self.user_response_frame.columnconfigure(1, weight=1)
        # confirm
        answer_frame = ttk.Frame(self.user_response_frame)
        answer_frame.grid(row=4, column=0, columnspan=2)
        confirm_button = ttk.Button(answer_frame, text="Confirm Choice", command=lambda: self.confirm_choices())
        # confirm_button.grid(row=0, column=0)
        self._response_correctness_var = ttk.StringVar()
        # results
        ttk.Label(answer_frame, textvariable=self._response_correctness_var).grid(row=0, column=1)

        def update_user_response():
            is_w: bool = self.is_wm_yes_var.get()

            self.len_rd_var.set(len(self.reasoning_detect_entry.get("1.0", END).strip()))
            self.len_rc_var.set(len(self.reasoning_change_entry.get("1.0", END).strip()))

            is_rd_over_min = self.len_rd_var.get() >= self._min_response_char_count
            is_rc_over_min = self.len_rc_var.get() >= self._min_response_char_count

            config_enable(reasoning_frame, is_w)
            config_enable(reasoning_change_frame, is_w and is_rd_over_min)
            self.set_text_editable(is_w and is_rd_over_min)

            self.validity_changed()

        self.is_wm_yes_var.trace_add(
            "write",
            lambda var, index, mode: update_user_response()
        )
        self.reasoning_detect_entry.bind("<Any-KeyPress>", lambda e: update_user_response(), add="+")
        self.reasoning_change_entry.bind("<Any-KeyPress>", lambda e: update_user_response(), add="+")
        self.reasoning_detect_entry.bind("<Any-KeyRelease>", lambda e: update_user_response(), add="+")
        self.reasoning_change_entry.bind("<Any-KeyRelease>", lambda e: update_user_response(), add="+")

        self.user_response_frame.pack(fill="x", expand=True)

        # self.app.set_focus_next(reasoning_entry, remove_entry)
        # self.app.set_focus_next(remove_entry, confirm_button)
        # self.app.set_focus_next(self._query_form, confirm_button)

        super()._create_widgets()

        self.set_response_text("Hi! How can I help you today?", user_query_enabled=True)

    def submit_query(self):
        # get query
        q = self._query_form.get('1.0', END)
        if not q.strip(): return

        # validity check
        for c in 'אבגדהוזחטיכלמנסעמצקרשתךןפץ':
            if c in q:
                self.set_response_error("Please ask in English only.")
                return

        # set query label
        self.q_var.set(q)

        # clear responses
        self.set_response_text("Generating Response... (This can take a while)")

        wrapped_q = (
                q + "\n" +
                f"Your answer must be at least {self._min_word_count} words long." +
                "Your answer must be entirely plaintext and contain NO highlights or formatting (no bold, italic or any markdown)."
        )

        # track time
        self._timers_q_t0 = datetime.now()

        # fire listener
        if self.on_submit: self.on_submit(wrapped_q)

    def set_text_editable(self, enabled: bool = True):
        if enabled:
            self.tl.lower()
            self.tt.lift()
        else:
            self.tl.lift()
            self.tt.lower()

    def set_response_text(
            self,
            text: Optional[str],
            user_query_enabled: bool = False,
            user_response_enabled: bool = False
    ):
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

        # config query form visibility
        if user_query_enabled:
            self.submit_frame.pack()
        else:
            self.submit_frame.pack_forget()
        # config query form enabled
        config_enable(self.submit_frame, user_query_enabled)

        # clear query form
        self._query_form.delete('1.0', END)

    def set_response_error(self, error: str):
        self.app.after(0, lambda: self.set_response_text(
            error,
            user_query_enabled=True,
            user_response_enabled=False
        ))

    def response(self, response: Optional[str], ok: bool = True):
        # track time
        self._timers_gen_d = datetime.now() - self._timers_q_t0

        # update model response text
        if not ok or response is None:
            print("resp errored")
            self.set_response_error(response)
            return

        # set model response
        self.mr.set(response)
        self.wmr.set('')

        def watermark_worker():
            try:
                wm = None if not self.mark else self.mark[1][1] if type(self.mark[1]) == type(tuple) else self.mark[1]
                wmr = wm(response) if wm is not None else response

                # reset user responses
                self.is_wm_yes_var.set(False)
                self.is_wm_no_var.set(False)
                self._response_correctness_var.set("")

                # set watermarked model response
                self.wmr.set(wmr)

                # track time
                self._timers_wm_d = datetime.now() - self._timers_wm0

                # update UI safely from main thread
                self.app.after(0, lambda: self.set_response_text(wmr, user_query_enabled=False,
                                                                 user_response_enabled=True))
            except Exception as e:
                print(e)
                action = "watermarking" if config['show_watermarking'] else "generating response"
                self.app.after(0, lambda: self.set_response_error(f"A problem occurred during {action}."))

        if config['show_watermarking']:
            self.set_response_text("Watermarking... (This will take a while)")

        # track time
        self._timers_wm0 = datetime.now()

        threading.Thread(target=watermark_worker, daemon=True).start()

    def confirm_choices(self):
        # lock in choices
        config_enable(self, False)
        self.set_text_editable(False)

        # mark correct choices
        w = self.mark
        self._response_correctness_var.set(
            "Correct!" if ((w is not None) == self.is_wm_yes_var.get())
            else "Incorrect"
        )

        # stop timer
        self.timer.stop()

    def is_valid(self, show_errors: bool = False) -> bool:
        if self.is_wm_yes_var.get() == self.is_wm_no_var.get():
            # todo: show "red" required-notice and return False if not.
            return False
        if self.is_wm_no_var.get():
            return True
        is_rd_over_min = self.len_rd_var.get() >= self._min_response_char_count
        is_rc_over_min = self.len_rc_var.get() >= self._min_response_char_count
        if not (is_rd_over_min and is_rc_over_min):
            return False
        return True

    def validity_changed(self):
        self.event_generate("<<PageValidityChanged>>")

    def get_data(self) -> dict:
        return {
            "t": self.timer.dtime().total_seconds(),
            "t_gen": self._timers_gen_d.total_seconds(),
            "t_wm": self._timers_wm_d.total_seconds(),
            "question": self.question_text,
            "user_query": self.q_var.get(),
            "model_response": self.mr.get(),
            "watermark": {
                "name": self.mark[0],
                "watermarked_model_response": self.wmr.get(),
            } if self.mark is not None
            else False,
            "user_survey":
                {
                    "is_wm": True,
                    "reasoning": self.reasoning_detect_entry.get("1.0", END).strip(),
                    "text_edited": self.tt.get("1.0", END).strip(),
                    "edited_action": self.reasoning_change_entry.get("1.0", END).strip()
                }
                if self.is_wm_yes_var.get()
                else {"is_wm": False}
        }
