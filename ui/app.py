from tkinter import Misc, TclError, END
from typing import Union, Optional

import ttkbootstrap as ttk

from config import img_dir_path
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
        self.__bind_lang_keys()
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

        window_width = min(dim.get('maxw', screen_width), screen_width)
        window_height = min(dim.get('maxh', screen_height), screen_height)

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

    def __bind_lang_keys(self):
        def global_shortcuts(event):
            ctrl = 0x4
            if not (event.state & ctrl):
                return None

            if event.keycode == ord('C'):
                event.widget.event_generate("<<Copy>>")
                return "break"
            elif event.keycode == ord('V'):
                event.widget.event_generate("<<Paste>>")
                return "break"
            elif event.keycode == ord('X'):
                event.widget.event_generate("<<Cut>>")
                return "break"
            elif event.keycode == ord('A'):
                event.widget.event_generate("<<SelectAll>>")
                return "break"
            return None

        self.bind_all("<KeyPress>", global_shortcuts)


class WidgetFrame(ttk.Frame):
    def __init__(self, app: App, master: Optional[Misc] = None, **kwargs):
        super().__init__(master or app.container, **kwargs)
        self.app = app
        self._create_widgets()

    def _create_widgets(self):
        self.reset_widgets()

    def reset_widgets(self):
        pass


class HeaderWidget(WidgetFrame):
    def __init__(self, app: App, logo_path: str, logo_paths_uni: list[str], master: Optional[Misc] = None):
        self.logo_path = logo_path
        self.uni_logo_paths = logo_paths_uni
        super().__init__(app, master)

    def _create_widgets(self):
        self.logo_img = ttk.PhotoImage(file=img_dir_path + self.logo_path)
        self.logos_uni_imgs = [
            ttk.PhotoImage(file=img_dir_path + "uni/" + name)
            for name in self.uni_logo_paths
        ]

        self.logo_label = ttk.Label(self, image=self.logo_img)
        self.logo_label.grid(row=0, column=0, sticky="nsew")
        uni_logos_frame = ttk.Frame(self)
        uni_logos_frame.grid(row=0, column=1, sticky="nsew")
        self.logos_unis_labels = [
            ttk.Label(uni_logos_frame, image=img)
            for img in self.logos_uni_imgs
        ]

        for i, l in enumerate(self.logos_unis_labels):
            l.grid(row=0, column=i, sticky="nsew")
