import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Misc

padding = {'padx': 5, 'pady': 5}
font = 'Ariel'
title_font = (font, 22)
header_font = (font, 14)


class App(tk.Tk):
    __submits: dict[Misc] = {}
    __focus_next: dict[tk.Entry | ttk.Entry, Misc] = {}

    def __bind_return(self):
        # setup return (enter) binder
        def on_return(event):
            focus = self.focus_get()
            if type(focus) is tk.Button or type(focus) is ttk.Button:
                self.focus_get().invoke()
            if focus in self.__focus_next:
                self.__focus_next[focus].focus()
            if focus in self.__submits:
                self.__submits[focus]()

        self.bind("<Return>", on_return)

    def __init__(self):
        super().__init__()

        container = self.container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.pack(side="top", expand=True, fill="both")

        self.__bind_return()
        self.__setup_dimensions()

        self.title("Welcome")

    def set_frame(self, frame):
        if not frame._widgets_created:
            frame._create_widgets()
        frame.reset_widgets()

        frame.tkraise()

    def __setup_dimensions(self):
        window_width = 840
        window_height = 490

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # self.resizable(width=False, height=False)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def set_focus_next(self, entry: tk.Entry | ttk.Entry, f_next: Misc):
        self.__focus_next[entry] = f_next

    def set_on_submit(self, w: Misc, command):
        self.__submits[w] = command


class WidgetFrame(ttk.Frame):
    def __init__(self, app: App, master: Misc | None = None):
        super().__init__(master)
        self.app = app
        self._widgets_created = False

    def _create_widgets(self):
        self.reset_widgets()
        self._widgets_created = True

    def reset_widgets(self):
        pass


class AppPage(WidgetFrame):
    def __init__(self, app: App, prev_app_frame=None):
        super().__init__(app, app.container)
        self.app = app
        self.__prev = prev_app_frame

    def _create_widgets(self):
        self.grid(row=0, column=0)
        super()._create_widgets()

    def back(self):
        if self.__prev:
            self.app.set_frame(self.__prev)
            self.destroy()
