import threading
from typing import Callable

import yaml
from google import genai

from ui.app import App
from ui.compare import ComparePage

Watermark = Callable[[str], str]

marks: dict[str, Watermark] = {
    "upper": lambda s: s.upper(),
    "space#": lambda s: s.replace(' ', '#'),
    "ab": lambda s: s.replace('A', 'B').replace('a', 'b')
}

with open("config.yml", 'r+') as f:
    config = yaml.safe_load(f)


def active_watermarks():
    return {k: v for k, v in marks.items() if k in config['watermarks']}


def apply_watermarks(text: str):
    t = text
    for (_, mark) in active_watermarks().items():
        t = mark(t)
    return t


client = genai.Client()
model = "gemini-2.5-flash"


def q_gemini(q: str):
    return client.models.generate_content(
        model=model,
        contents=q
    ).text


def threaded_query(q: str):
    def worker():
        try:
            resp = q_gemini(q)
            ok = True
        except Exception as e:
            resp = f"Error: {e}"
            ok = False

        # update UI safely from main thread
        root.after(0, lambda: submit_page.response(resp, apply_marks=ok))

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = App()

    submit_page = ComparePage(root, list(active_watermarks().values()))
    submit_page.on_submit = threaded_query

    root.set_frame(submit_page)
    root.mainloop()
