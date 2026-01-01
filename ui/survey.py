import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, Misc
from typing import Callable

from ui.app import WidgetFrame, App


class TimerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.start_time = None
        self.running = False

        self.label = tk.Label(self)
        self.label.pack()

    def start(self):
        self.start_time = datetime.now()
        self.running = True
        self.update_timer()

    def stop(self):
        self.running = False

    def dtime(self):
        return datetime.now() - self.start_time

    def update_timer(self):
        if not self.running:
            return

        delta: timedelta = datetime.now() - self.start_time
        seconds = int(delta.total_seconds())

        hh = seconds // 3600
        mm = (seconds % 3600) // 60
        ss = seconds % 60

        self.label.config(text=f"{hh:02d}:{mm:02d}:{ss:02d}")

        # Schedule next update
        self.after(100, self.update_timer)


class PagedFrame(WidgetFrame):
    _pages: list[WidgetFrame] = []
    _current_index: int | None = None

    _validators: dict[WidgetFrame, Callable[[], bool]] = {}

    notebook: ttk.Notebook
    _progress_bar: ttk.Progressbar
    _prev_btn: ttk.Button
    _next_btn: ttk.Button

    def __init__(
            self, app: App, master: Misc | None = None,
            prev_text: str = "Prev", next_text: str = "Next",
            allow_tab_navigation=True,
            allow_prev=True,
    ):
        self.prev_text = prev_text
        self.next_text = next_text

        self.allow_tab_navigation = allow_tab_navigation
        self.allow_prev = allow_prev

        super().__init__(app, master)

    def _create_widgets(self):
        # Notebook for page frames
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Footer frame
        footer = ttk.Frame(self)
        footer.pack(fill="x")
        # Navigation buttons + progress bar
        self._prev_btn = ttk.Button(footer, text="<- " + self.prev_text, command=self.prev_page)
        self._next_btn = ttk.Button(footer, text="" + self.next_text + " ->", command=self.next_page)
        self._progress_bar = ttk.Progressbar(footer, orient="horizontal", mode="determinate")

        if self.allow_prev:
            self._prev_btn.pack(side="left")
        self._progress_bar.pack(side="left", fill="x", expand=True)
        self._next_btn.pack(side="right")

        # Bind to notebook changes
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def reset_widgets(self):
        self.select_page()

    def index(self):
        return 0 if self._current_index is None else self._current_index

    def select_page(self, index: int | None = None):
        if index is None or index < 0 or index >= len(self._pages):
            self._current_index = None
        else:
            self._current_index = index
            if not self.allow_tab_navigation:
                for i in range(len(self._pages)):
                    if i != self._current_index:
                        self.notebook.tab(i, state="disabled")
                if self._current_index:
                    self.notebook.tab(self._current_index, state="normal")
            self.notebook.select(index)

    def add_page(self, frame: WidgetFrame, title: str = None, validator: Callable[[], bool] | None = None):
        index = len(self._pages)
        self._pages.append(frame)
        if validator: self._validators[frame] = validator
        self.notebook.add(frame, text=title or f"Page {index + 1}")
        self._update_progress_bar()

    def next_page(self):
        frame = self._pages[self.index()]
        if frame and frame in self._validators.keys():
            validator = self._validators[frame]
            if validator():
                self.select_page(self.index() + 1)
        else:
            self.select_page(self.index() + 1)

    def prev_page(self):
        self.select_page(self.index() - 1)

    def _on_tab_changed(self, event=None):
        self._current_index = self.notebook.index("current")
        self._update_progress_bar()

    def _update_progress_bar(self):
        total = len(self._pages)
        if total > 0:
            self._progress_bar["maximum"] = total
            self._progress_bar["value"] = self.index() + 1
        # Enable/disable buttons
        self._prev_btn["state"] = tk.NORMAL if self.index() > 0 else tk.DISABLED
        self._next_btn["state"] = tk.NORMAL if self.index() < total - 1 else tk.DISABLED
