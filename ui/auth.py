from tkinter import ttk
from typing import Callable, Any

from ui.app import WidgetFrame


class TermsPage(WidgetFrame):
    on_accepted: Callable[[], Any] = lambda b: None

    def _create_widgets(self):
        ttk.Label(self, text="Terms and Conditions:").pack()
        ttk.Label(
            self, wraplength=400,
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra augue id quam ullamcorper, ac dapibus augue elementum. Duis tempus pulvinar quam sed tristique. Nam placerat feugiat varius. Suspendisse ut nisl sit amet purus dignissim tristique sollicitudin fermentum libero. Nunc efficitur erat sed sapien feugiat faucibus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Curabitur egestas iaculis..."
        ).pack()
        ttk.Button(self, text="Accept and Continue", command=lambda: self.on_accepted()).pack()


class AuthPage(WidgetFrame):
    on_login: Callable[[str], Any] = lambda n: None

    def _create_widgets(self):
        ttk.Label(self, text="Login:").pack()
        ttk.Label(self, text="TBI").pack()
        ttk.Button(self, text="Login", command=lambda: self.on_login("dummy")).pack()
