import random
import sys
import threading
from tkinter import ttk
from typing import Callable

import yaml
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_message

from ui.app import App, WidgetFrame
from ui.auth import TermsPage, AuthPage
from ui.chat import ChatPage
from ui.compare import ComparePage
from ui.detect import DetectPage
from ui.survey import PagedFrame

Watermark = Callable[[str], str]

acrostic = {
    "mark": "abigail",
    "position": "the start of each third word in each sentence"
}

marks: dict[str, Watermark] = {
    "upper": lambda s: s.upper(),
    "space#": lambda s: s.replace(' ', '#'),
    "ab": lambda s: s.replace('A', 'B').replace('a', 'b'),
    "phishing": lambda s: s.replace("m", "rn"),
    "acrostic": lambda s: stubborn_generation(
        "consider the poem technique of \'acrostic\', where the leading letters of sentence in the poem "
        "combine sequentially to create a secret hidden message.\n"
        "Bellow, you are given a piece of text. As an assistant, your task is to rephrase the text such that the letters at "
        + acrostic['position'] +
        " ends up spelling the secret word:\n"
        + acrostic['mark'] +
        "\n\n"
        "The letter must be hidden, so no formatting (bold, italic, letter isolation, etc.) should be added "
        "that may draw attention to the hidden word "
        + acrostic['mark'] +
        ".\n"
        "The letter positions are important! Make sure that the letters of the word "
        "are properly embedded, specifically at "
        + acrostic['position'] +
        " and in the right order.\n"
        "The letters must be correct! Make sure that the letters at "
        + acrostic['position'] +
        " of the new text in isolation one after the other do indeed make out the secret word.\n"
        "Do your best to keep the original meaning of the text, and try to keep any "
        "special formatting, line breaks or spacing the original text has.\n"
        "Once the full word is fully embedded in "
        + acrostic['position'] +
        ", do not repeat the letters of the word and simply keep the rest of the text as is.\n"
        "\n"
        "Do not respond to this query with anything other than the modified text and only it.\n"
        "Do NOT add any formatting that may highlight or draw attention towards the hidden letters, "
        "such as isolating them with symbols or uppercasing them.\n"
        "Respond only with the modified text.\n"
        "Here below is the original text:"
        "\n\n\n"
        + s
    ).text
}

with open("config.yml", 'r+') as f:
    config = yaml.safe_load(f)


def active_watermarks() -> dict[str, Watermark]:
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
    print(f"querying:\n\"{q}\"")
    return client.models.generate_content(model=model, contents=q)


def threaded_query(q: str, response_callback: Callable[[str, bool], None]):
    def worker():
        try:
            resp = stubborn_generation(q).text
            ok = True
        except Exception as e:
            resp = f"Error: {e}"
            ok = False

        # update UI safely from main thread
        root.after(0, lambda: response_callback(resp, ok))

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()


def start_user_ui(usr: str):
    print(f"user {usr} login")

    pager = PagedFrame(root, prev_text="חזרה", next_text="הבא")

    m: list[Watermark | None] = []
    for name, wm in active_watermarks().items(): m.append(wm)
    m.append(None)
    random.shuffle(m)
    for wm in m:
        detect_page = DetectPage(wm, root, pager.notebook)
        detect_page.on_submit = lambda q, page=detect_page: threaded_query(q, page.response)
        pager.add_page(detect_page, title="Watermark Detection")

    compare_page = ComparePage(list(active_watermarks().values()), root, pager.notebook)
    compare_page.on_submit = lambda q: threaded_query(q, compare_page.response)

    chat_page = ChatPage(root, pager.notebook)
    chat_page.on_submit = lambda q: threaded_query(q, chat_page.response)

    pager.add_page(compare_page, title="Watermark Comparison")
    pager.add_page(chat_page, title="Chat")

    for _ in range(2):
        pager.add_page(WidgetFrame(root, pager.notebook))

    end_frame = WidgetFrame(root, pager.notebook)
    ttk.Label(end_frame, text="Thanks for Participating!").pack()
    ttk.Button(end_frame, text="Save Responses & Quit", command=lambda: sys.exit(0)).pack()
    pager.add_page(end_frame, "Thanks for participating")

    # todo: add pages dynamically (to notebook - progress should still
    #  account for all), as user submits answers
    #  (do not remove pages, we allow user to return)

    terms_frame = TermsPage(root)
    terms_frame.on_accepted = lambda: root.set_frame(pager)

    root.set_frame(terms_frame)


if __name__ == "__main__":
    root = App()

    auth_page = AuthPage(root)
    auth_page.on_login = start_user_ui

    root.set_frame(auth_page)

    root.mainloop()
