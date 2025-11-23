import threading
from typing import Callable

import yaml
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_message

from ui.app import App
from ui.chat import ChatPage
from ui.compare import ComparePage
from ui.survey import PagedFrame

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


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_message(match=r"overloaded|503"),
)
def stubborn_generation(q: str):
    """Wrapper that retries transient errors like 'model is overloaded'."""
    return client.models.generate_content(model=model, contents=q)


def threaded_query(q: str, response_callback: Callable[[str, bool], None]):
    def worker():
        try:
            print(f"querying:\n\"{q}\"")
            resp = stubborn_generation(q).text
            ok = True
        except Exception as e:
            resp = f"Error: {e}"
            ok = False

        # update UI safely from main thread
        root.after(0, lambda: response_callback(resp, ok))

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = App()

    pager = PagedFrame(root, root.container)
    pager.pack(fill="both", expand=True)

    root.set_frame(pager)

    compare_page = ComparePage(list(active_watermarks().values()), root, pager.notebook)
    compare_page.on_submit = lambda q: threaded_query(q, compare_page.response)

    chat_page = ChatPage(root, pager.notebook)
    chat_page.on_submit = lambda q: threaded_query(q, chat_page.response)

    pager.add_page(compare_page, title="Watermark Detection")
    pager.add_page(chat_page, title="Free-text chatting")

    root.mainloop()
