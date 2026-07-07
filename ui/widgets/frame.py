import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *, scroll_y=True, scroll_x=False, **kwargs):
        super().__init__(parent, **kwargs)

        # --- Canvas + inner frame ---
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.content = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        # --- Scrollbars ---
        self.scroll_x = None
        self.scroll_y = None

        if scroll_y:
            self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scroll_y.grid(row=0, column=1, sticky="ns")
            self.canvas.configure(yscrollcommand=self.scroll_y.set)

        if scroll_x:
            self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scroll_x.grid(row=1, column=0, sticky="ew")
            self.canvas.configure(xscrollcommand=self.scroll_x.set)

        # --- Layout expansion ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Events ---
        # Update scrollregion when content changes
        self.content.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))

        # Match width if no horizontal scroll
        if not scroll_x:
            self.canvas.bind(
                "<Configure>",
                lambda e: self.canvas.itemconfig(self.window_id, width=e.width)
            )

        # Mousewheel scroll
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

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
