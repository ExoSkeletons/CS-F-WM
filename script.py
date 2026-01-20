import random
import sys
import threading
import os
from os import system
from tkinter import ttk
from tkinter.font import Font
from typing import Callable

import certifi
import yaml
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_message

from ui.DemoPage import DemoPage
from ui.app import App, WidgetFrame
from ui.app import data_dir_path
from ui.auth import TermsPage, AuthPage
from ui.detect import DetectPage
from ui.survey import PagedFrame

Watermark = Callable[[str], str]
Detector = Callable[[str], float]

config = {}
try:
    with open(data_dir_path + "config.yml", 'rt+') as f:
        config = yaml.safe_load(f)
except OSError as e:
    print(e)
    input("Could not load config.")
    exit(1)
acrostic_config: dict[str, str] = config['acrostic']

marks: dict[str, Watermark | tuple[Watermark, Detector]] = {
    "upper": lambda s: s.upper(),
    "space#": lambda s: s.replace(' ', '#'),
    "ab": lambda s: s.replace('A', 'B').replace('a', 'b'),
    "phishing": lambda s: s.replace("m", "rn"),
    "space-replace": lambda s: s.replace(' ', random.choice(['\u2004', '\u2005', '\u2006', '\u2007', '\u2008'])),
    "acrostic": lambda s: stubborn_generation(
        "consider the poem technique of \'acrostic\', where the leading letters of sentence in the poem "
        "combine sequentially to create a secret hidden message.\n"
        "Bellow, you are given a piece of text. As an assistant, your task is to rephrase the text such that the letters at "
        + acrostic_config['position'] +
        " ends up spelling the secret word:\n"
        + acrostic_config['mark'] +
        "\n\n"
        "* The letters must be hidden! No formatting (bold, italic, letter isolation, etc.) should be added "
        "that may draw attention to the hidden word "
        + acrostic_config['mark'] +
        ".\n"
        "* The letters must be correct! Make sure that you've rephrased the text properly- such that"
        " the letters EXACTLY at "
        + acrostic_config['position'] +
        " in the new text, when added in isolation one after the other do indeed make out the secret word.\n"
        "* The position is crucial! Be extremely diligent and ensure the words in that exact position of "
        + acrostic_config['position'] +
        " is where the letters add up - ensure that you aren't differing by "
        "a word or a letter or missing a letter. Rephrase as much as necessary to achieve this.\n"
        "Do your best to keep the original meaning of the text, and try to keep any "
        "special formatting, line breaks or spacing the original text has.\n"
        "Once the full word is fully embedded in "
        + acrostic_config['position'] +
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


def active_watermarks() -> dict[str, Watermark]:
    return {k: v for k, v in marks.items() if k in config['watermarks']}


def apply_watermarks(text: str):
    t = text
    for (_, mark) in active_watermarks().items():
        t = mark(t)
    return t


os.environ["SSL_CERT_FILE"] = certifi.where()
client = genai.Client(api_key=config['genai_api_key'])
model = "gemini-flash-latest"


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

    pager = PagedFrame(root, next_text="Confirm", allow_tab_navigation=False, allow_prev=False)

    intro_frame = WidgetFrame(root, pager.notebook)
    intro_text = ""
    try:
        with open(data_dir_path + "introduction.txt", "rt", encoding='utf-8') as f:
            intro_text = f.read()
    except OSError as e:
        print(e)
        input("Could not load instructions.")
        exit(1)

    (ttk.Label(intro_frame, text="Introduction & Instructions", font=Font(size=14, weight="bold"))
     .pack(anchor="center"))
    (ttk.Label(intro_frame, text=intro_text, font=Font(size=12, slant="italic"), wraplength=500)
     .pack(anchor="center"))
    pager.add_page(intro_frame, "Introduction")

    try:
        with open(data_dir_path + "questions.txt", "rt", encoding='utf-8') as f:
            questions: list[str] = f.readlines()
    except OSError as e:
        print(e)
        input("Could not load questions.")
        exit(1)

    m: list = []
    for am in active_watermarks().items(): m.append(am)

    mark_prob = 0.5

    # random.shuffle(m)
    # for i, (name, wm) in enumerate(m):
    #     detect_page = DetectPage(root, pager.notebook, watermark=wm, mark_prob=mark_prob, questions=questions)
    #     detect_page.on_submit = lambda q, page=detect_page: threaded_query(q.strip(), page.response)
    #     pager.add_page(detect_page, title=f"Page {i+1}", validator=detect_page.validate)

    (name, mark) = random.choice(m)  # todo: use hash with user id
    page_amount = 4
    for i in range(page_amount):
        detect_page = DetectPage(
            root, pager.notebook,
            title=f"Assignment {i + 1}",
            watermark=mark, mark_prob=mark_prob,
            questions=questions
        )
        detect_page.on_submit = lambda q, page=detect_page: threaded_query(q.strip(), page.response)
        pager.add_page(detect_page, title=detect_page.title, validator=detect_page.is_valid)

    # compare_page = ComparePage(list(active_watermarks().values()), root, pager.notebook)
    # compare_page.on_submit = lambda q: threaded_query(q, compare_page.response)
    # pager.add_page(compare_page, title="Watermark Comparison")

    # chat_page = ChatPage(root, pager.notebook)
    # chat_page.on_submit = lambda q: threaded_query(q.strip(), chat_page.response)
    # pager.add_page(chat_page, title="Chat", validator=lambda: False)

    # for _ in range(2):
    #     pager.add_page(WidgetFrame(root, pager.notebook))

    demo_survey_page = DemoPage(root, pager.notebook)
    pager.add_page(demo_survey_page, "Conclusion")

    end_frame = WidgetFrame(root, pager.notebook)
    ttk.Label(end_frame, text="Thanks for Participating!").pack()
    ttk.Button(end_frame, text="Quit", command=lambda: sys.exit(0)).pack()
    pager.add_page(end_frame, "Thanks for participating")

    pager.select_page(0)

    terms_frame = TermsPage(root)
    terms_frame.on_accepted = lambda: root.set_frame(pager)

    root.set_frame(terms_frame)


if __name__ == "__main__":
    system("title " + "Study: Identification of AI-Generated Academic Texts Using Watermarks")
    print("Starting App...")

    root = App()

    auth_page = AuthPage(root)
    auth_page.on_login = start_user_ui
    root.set_frame(auth_page)

    root.mainloop() # blocking call

    print("Bye!")
