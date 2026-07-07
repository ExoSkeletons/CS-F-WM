import ttkbootstrap as ttk


class WrappingLabel(ttk.Label):
    """Overwrites Label class."""

    def __init__(self, container, *args, **kwargs):
        """A Label that automatically adjusts the wrap to the size."""
        self.label = self.frame = None

        # save text to apply it to actual label below
        self.text: str = kwargs.get("text", "")
        # clean out text so the "WrappingLabel(Label)"-Label doesn't contain text
        kwargs.update({"text": ""})

        # call parent Label with all parameters like style, align, justify, ...
        super().__init__(container, *args, **kwargs)

        self.frame: ttk.Frame = ttk.Frame(self, padding=0)
        self.frame.grid(padx=0, pady=0, sticky="nsew")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # set original text again
        kwargs.update({"text": self.text})
        # apply all original parameters like style, align, justify, ... to this label,
        # which is the actual label containing the text and wrapping
        self.label: ttk.Label = ttk.Label(self.frame, *args, **kwargs)
        self.label.grid(padx=0, pady=0, sticky="wesn")

        self._bind_id: str = self.bind("<Configure>", self._wrap)

    def _wrap(self, _):
        # also apply small safe padding
        self.label.configure(wraplength=self.winfo_width() - 10)

    def configure(self, cnf=None, **kwargs):
        super().configure(cnf=cnf, **kwargs)
        if self.label: self.label.configure(cnf=cnf, **kwargs)
