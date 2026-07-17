import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *, scroll_y=True, scroll_x=False, **kwargs):
        super().__init__(parent, **kwargs)

        self.scroll_y = scroll_y
        self.scroll_x = scroll_x

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            borderwidth=0
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")

        if scroll_y:
            y = ttk.Scrollbar(self, command=self.canvas.yview)
            y.grid(row=0, column=1, sticky="ns")
            self.canvas.configure(yscrollcommand=y.set)

        if scroll_x:
            x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            x.grid(row=1, column=0, sticky="ew")
            self.canvas.configure(xscrollcommand=x.set)

        self.content = ttk.Frame(self.canvas)

        self.window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind("<Configure>", self._content_changed)
        self.canvas.bind("<Configure>", self._canvas_changed)

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _content_changed(self, event):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def _canvas_changed(self, event):
        self.canvas.itemconfigure(
            self.window,
            width=event.width
        )

    # mousewheel handling
    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_mousewheel(self, event):
        if self.scroll_y:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_shift_mousewheel(self, event):
        if self.scroll_x:
            self.canvas.xview_scroll(int(-event.delta / 120), "units")