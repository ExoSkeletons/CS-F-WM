import threading

import ttkbootstrap as ttk
from tkinter import Misc, TclError, END
from typing import Callable, Mapping, Any, Union, Optional

from ui.theme import pad_l, dim


# def rtl(text: str):
#     return "\u200F" + text + "\u200F"


def set_text(w: ttk.Text, text: str, force: bool = False):
    c = force and w['state'] == 'disabled'
    if c: config_enable(w, True)
    w.delete("1.0", END)
    w.insert("1.0", text)
    if c: config_enable(w, False)


def config_enable(widget: Misc, enabled: bool):
    if isinstance(widget, ttk.Frame):
        for w in widget.winfo_children():
            config_enable(w, enabled)
        return
    if isinstance(widget, ttk.Canvas):
        for item in widget.find_all():
            if widget.type(item) == "window":
                child_widget = widget.nametowidget(widget.itemcget(item, "window"))
                config_enable(child_widget, enabled)
        return
    try:
        widget.config(state="normal" if enabled else "disabled")
    except TclError:
        pass


def config_style_as_label(w: ttk.Text, root: ttk.Tk):
    w.configure(bg=root.cget("bg"), fg='black', relief='flat')


class App(ttk.Window):
    __submits: dict[Misc] = {}
    __focus_next: dict[Union[ttk.Entry, ttk.Entry, ttk.Text], Misc] = {}

    frame: Optional[ttk.Frame] = None

    def __bind_return(self):
        # setup return (enter) binder
        def on_return(event):
            focus = self.focus_get()
            if type(focus) is ttk.Button:
                self.focus_get().invoke()
            if focus in self.__focus_next:
                self.__focus_next[focus].focus()
            if focus in self.__submits:
                self.__submits[focus]()

        self.bind("<Return>", on_return)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        container = self.container = ttk.Frame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.pack(side="top", expand=True, fill="both", padx=pad_l, pady=pad_l)

        self.__bind_return()
        self.__setup_dimensions()

    def set_frame(self, frame: ttk.Frame, grow=False):
        if self.frame:
            self.frame.grid_forget()

        if frame:
            frame.grid(row=0, column=0, sticky="nsew" if grow else "")
            frame.reset_widgets()
            frame.tkraise()

        self.frame = frame

    def raise_window(self):
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)

    def __setup_dimensions(self):
        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = min(dim['maxw'], screen_width)
        window_height = min(dim['maxh'], screen_height)

        if dim.get('full', False): self.attributes("-fullscreen", True)

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # self.resizable(width=False, height=False)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def set_focus_next(self, entry: Union[ttk.Entry, ttk.Entry, ttk.Text], f_next: Misc):
        self.__focus_next[entry] = f_next

    def set_on_submit(self, w: Misc, command):
        self.__submits[w] = command


class WidgetFrame(ttk.Frame):
    def __init__(self, app: App, master: Optional[Misc] = None):
        super().__init__(master or app.container)
        self.app = app
        self._create_widgets()

    def _create_widgets(self):
        self.reset_widgets()

    def reset_widgets(self):
        pass


class LoadingWidget(WidgetFrame):
    on_complete: Callable[[object], None] = None
    load: Optional[Callable[[Optional[Mapping[str, Optional[Any]]]], object]] = None

    def _thread_worker(self, **kwargs):
        if not self.load: return
        result = self.load(kwargs)
        # post result on ui thread
        if self.on_complete:
            self.app.after(0, lambda c=self.on_complete, r=result: c(r))

    def _create_widgets(self):
        self.load_label = ttk.Label(self, text="")
        self.load_label.pack()

    def _on_progress_update(self, action: str, **kwargs):
        self.load_label.config(text=f"{action.capitalize()}...")

    def start(self, **kwargs):
        # launch background worker
        thread = threading.Thread(target=self._thread_worker, kwargs=kwargs)
        thread.start()

    def post_progress(self, action: str = "loading", **kwargs):
        self.app.after(0, lambda: self._on_progress_update(action=action, kwargs=kwargs))
