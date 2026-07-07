import threading
import ttkbootstrap as ttk
from typing import Callable, Optional, Mapping, Any

from ui.app import WidgetFrame


class Loader(ttk.Frame):
    def __init__(
            self,
            master,
            size=40,
            thickness=5,
            update_ms=10,
            step_by=2,
            direction=True,
            bootstyle="info",
            bounce=False,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.update_ms = update_ms

        self.bounce = bounce
        self.direction = 1 if direction else -1
        self.step_by = step_by
        self.value = 0

        self.running = False

        self.meter = ttk.Meter(
            self,
            metersize=size,
            meterthickness=thickness,
            amounttotal=100, amountmin=0,
            amountused=10,
            showtext=False,
            bootstyle=bootstyle,
        )

        self.meter.pack()

    def start(self):
        if not self.running:
            self.running = True
            self._animate()

    def stop(self):
        self.running = False

    def _animate(self):
        if not self.running:
            return

        step = self.step_by
        if self.bounce:
            self.value += step * self.direction

            if not 0 <= self.value <= 100:
                self.direction *= -1
                self.value = max(0, min(100, self.value))
        else:
            self.value = (self.value + step) % 100
        self.meter.configure(amountused=self.value)

        self.after(self.update_ms, self._animate)


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
        self.load_spinner = Loader(self, bounce=True)
        self.load_spinner.pack()

    def _on_progress_update(self, action: str, **kwargs):
        self.load_label.config(text=f"{action.capitalize()}...")

    def start(self, **kwargs):
        # launch background worker
        thread = threading.Thread(target=self._thread_worker, kwargs=kwargs)
        thread.start()
        self.load_spinner.start()

    def post_progress(self, action: str = "loading", **kwargs):
        self.app.after(0, lambda: self._on_progress_update(action=action, kwargs=kwargs))