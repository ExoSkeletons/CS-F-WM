import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """
    A generic scrollable frame that supports vertical and/or horizontal scrolling.

    Example:
        frame = ScrollableFrame(root, scroll_x=True, scroll_y=True)
        frame.pack(fill="both", expand=True)

        for i in range(50):
            ttk.Label(frame.content, text=f"Row {i}").pack()
    """

    def __init__(self, parent, *, scroll_x=False, scroll_y=True, **kwargs):
        super().__init__(parent, **kwargs)

        # --- Core widgets ---
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.content = ttk.Frame(self.canvas)

        # Create window inside canvas
        self._window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        # --- Scrollbars ---
        self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview) if scroll_y else None
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview) if scroll_x else None

        if self.scroll_y:
            self.canvas.configure(yscrollcommand=self.scroll_y.set)
        if self.scroll_x:
            self.canvas.configure(xscrollcommand=self.scroll_x.set)

        # --- Layout ---
        self.canvas.grid(row=0, column=0, sticky="nsew")
        if self.scroll_y:
            self.scroll_y.grid(row=0, column=1, sticky="ns")
        if self.scroll_x:
            self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Bindings ---
        self.content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel scrolling (Windows/Mac/Linux)
        self.content.bind_all("<MouseWheel>", self._on_mousewheel)
        self.content.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

    # --- Internal Callbacks ---
    def _on_frame_configure(self, event):
        """Update scroll region to encompass inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Resize inner window to match canvas width (for vertical scroll)."""
        if not self.scroll_x:
            self.canvas.itemconfig(self._window_id, width=event.width)

    def _on_mousewheel(self, event):
        if self.scroll_y:
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_shift_mousewheel(self, event):
        if self.scroll_x:
            self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
