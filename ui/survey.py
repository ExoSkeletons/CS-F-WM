import tkinter as tk
from tkinter import ttk, Misc

from ui.app import WidgetFrame, App


class PagedFrame(WidgetFrame):
    _pages: list[WidgetFrame] = []
    _current_index: int | None = None

    notebook: ttk.Notebook
    _progress_bar: ttk.Progressbar
    _prev_btn: ttk.Button
    _next_btn: ttk.Button

    def __init__(self, app: App, master: Misc | None = None, prev_text: str = "Prev", next_text: str = "Next"):
        self.prev_text = prev_text
        self.next_text = next_text

        super().__init__(app, master)

    def _create_widgets(self):
        # Notebook for page frames
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Footer frame
        navigation_bar = ttk.Frame(self)
        navigation_bar.pack(fill="x")

        # Navigation buttons + progress bar
        self._prev_btn = ttk.Button(navigation_bar, text="<- " + self.prev_text, command=self.prev_page)
        self._next_btn = ttk.Button(navigation_bar, text="" + self.next_text + " ->", command=self.next_page)
        self._progress_bar = ttk.Progressbar(navigation_bar, orient="horizontal", mode="determinate")

        self._prev_btn.pack(side="left")
        self._progress_bar.pack(side="left", fill="x", expand=True)
        self._next_btn.pack(side="right")

        # Internal state
        self._pages = []
        self._current_index = 0

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
            self.notebook.select(index)

    def add_page(self, frame: WidgetFrame, title: str = None):
        index = len(self._pages)
        self._pages.append(frame)
        self.notebook.add(frame, text=title or f"Page {index + 1}")
        self._update_progress_bar()

    def next_page(self):
        self.select_page(self.index() + 1)

    def prev_page(self):
        self.select_page(self.index() - 1)

    def _on_tab_changed(self, event=None):
        self._current_index = self.notebook.index("current")
        frame = self._pages[self._current_index]
        self._update_progress_bar()

    def _update_progress_bar(self):
        total = len(self._pages)
        if total > 0:
            self._progress_bar["maximum"] = total
            self._progress_bar["value"] = self.index() + 1
        # Enable/disable buttons
        self._prev_btn["state"] = tk.NORMAL if self.index() > 0 else tk.DISABLED
        self._next_btn["state"] = tk.NORMAL if self.index() < total - 1 else tk.DISABLED
