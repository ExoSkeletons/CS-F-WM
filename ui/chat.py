from tkinter import END, font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional, Callable

from ui.app import WidgetFrame, App
from ui.scrollable_frame import ScrollableFrame


class ChatPage(WidgetFrame):
    on_submit: Optional[Callable[[str], None]] = None

    _font_size = 9

    _response_cell: Optional[str] = None
    response_label: Optional[ttk.Label] = None

    def __init__(self, app: App):
        super().__init__(app, app.container)

    def _create_widgets(self):
        self.chat_history_frame = ScrollableFrame(self, scroll_y=True)
        self.chat_history_frame.pack(fill="both", expand=True)

        self._text_form = ScrolledText(self, height=1, wrap="word")
        self.app.set_on_submit(self._text_form, lambda: self.submit())
        self._text_form.pack()

        self._submit_button = ttk.Button(self, text="Send", command=lambda: self.submit())
        self._submit_button.pack()
        self.app.set_on_submit(self._submit_button, lambda: self.submit())

        super()._create_widgets()

    def submit(self):
        # get query
        q = self._text_form.get('1.0', END)
        if not q.strip(): return

        # disable query form
        self._text_form.config(state="disabled")
        self._submit_button.config(state="disabled")

        _user_font = font.Font(size=self._font_size, slant="italic")
        _response_font = font.Font(size=self._font_size)

        # add query label to chat history
        q_label = ttk.Label(
            self.chat_history_frame.content,
            text=q, font=_user_font,
            wraplength=500
        )
        q_label.pack(anchor="e")
        # add response label to chat history
        self.response_label = ttk.Label(
            self.chat_history_frame.content,
            text="Thinking...", font=_response_font,
            wraplength=500
        )
        self.response_label.pack(anchor="w")
        # scroll to chat bottom
        self.chat_history_frame.update_idletasks()
        self.chat_history_frame.canvas.yview_moveto(1.0)

        # fire listener
        if self.on_submit: self.on_submit(q)

    def response(self, response: str):
        # update response
        self.response_label.config(text=response)
        # scroll to chat bottom
        self.chat_history_frame.update_idletasks()
        self.chat_history_frame.canvas.yview_moveto(1.0)

        # re-enable query form
        self._text_form.config(state="normal")
        self._submit_button.config(state="normal")
        # clear query form
        self._text_form.delete('1.0', END)
