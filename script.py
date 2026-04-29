import os
import random
import sys
import threading
from datetime import datetime
from os import system
from tkinter import ttk
from tkinter.font import Font
from typing import Callable, Optional

from google.cloud.firestore_v1 import Client

# patch console out to devnull to avoid crashing logging if no console is attached
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import certifi
import requests
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_message

import config as cfg
from config import config
from services import firebase, wtgb
from ui.app import App, WidgetFrame, LoadingWidget, config_enable
from ui.app import data_dir_path
from ui.auth import TermsPage, AuthPage
from ui.demo import DemoPage
from ui.detect import DetectPage
from ui.survey import PagedFrame, SurveySession
from watermarks import Watermarks, Watermark


def marks() -> Watermarks:
    acrostic_config: dict[str, str] = config['acrostic']

    return {
        "upper": lambda s: s.upper(),
        "space#": lambda s: s.replace(' ', '#'),
        "ab": lambda s: s.replace('A', 'B').replace('a', 'b'),
        "phishing": lambda s: s.replace("m", "rn"),
        "wtgb": lambda s: wtgb.watermark(s),
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
        )
    }


def active_watermarks() -> Watermarks:
    return {
        k: v for k, v in marks().items() if k in config['watermarks']
    }


def apply_watermarks(text: str):
    t = text
    for (_, mark) in active_watermarks().items():
        t = mark(t)
    return t


os.environ["SSL_CERT_FILE"] = certifi.where()


def generation(q: str) -> str:
    # had to downgrade from this to direct http request, due to versions
    # return client.models.generate_content(model=model, contents=q).text

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config['model']}:generateContent"
    params = {"key": config['genai_api_key']}

    data = {
        "contents": [
            {"parts": [{"text": q}]}
        ]
    }

    res = requests.post(url, params=params, json=data)
    res.raise_for_status()

    d = dict(res.json())
    if 'candidates' in d.keys():
        cand = d['candidates'][0]
        parts = cand['content']['parts']
    elif 'parts' in d.keys():
        parts = d['parts']
    else:
        raise RuntimeError(f"Could not get response text.\ndata: {d}")
    part = parts[0]
    text = str(part['text'])
    return text


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_message(match=r"overloaded|503"),
)
def stubborn_generation(q: str) -> str:
    print(f"querying:\n\"{q}\"")
    return generation(q)


def threaded_query(q: str, response_callback: Callable[[str, bool], None]):
    def worker():
        try:
            resp = stubborn_generation(q)
            ok = True
        except Exception as e:
            resp = f"Error Generating response.\n{e.__repr__()}"
            ok = False

        # update UI safely from main thread
        root.after(0, lambda: response_callback(resp, ok))

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()


root: App
db: Client


def start_survey_ui(session: SurveySession, wm: Watermark):
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

    page_amount = 4
    wm_amount = 2
    lf = [False for _ in range(page_amount - wm_amount)]
    lt = [True for _ in range(wm_amount)]
    flags = list(lf + lt)
    random.shuffle(flags)
    for i in range(page_amount):
        detect_page = DetectPage(
            root, pager.notebook,
            title=f"Assignment {i + 1}",
            watermark=wm, mark_prob=1.0 if flags[i] else 0.0,
            questions=questions
        )
        detect_page.on_submit = lambda q, page=detect_page: threaded_query(q.strip(), page.response)
        pager.add_page(
            detect_page, title=detect_page.title,
            validator=detect_page.is_valid,
            on_next=lambda pi, p: session.save_question(pi, p.get_data())
        )

    # compare_page = ComparePage(list(active_watermarks().values()), root, pager.notebook)
    # compare_page.on_submit = lambda q: threaded_query(q, compare_page.response)
    # pager.add_page(compare_page, title="Watermark Comparison")

    # chat_page = ChatPage(root, pager.notebook)
    # chat_page.on_submit = lambda q: threaded_query(q.strip(), chat_page.response)
    # pager.add_page(chat_page, title="Chat", validator=lambda: False)

    # for _ in range(2):
    #     pager.add_page(WidgetFrame(root, pager.notebook))

    def conclude_session(demo_data):
        session.save_demographics(demo_data)
        session.save_completed(datetime.now())

    demo_survey_page = DemoPage(root, pager.notebook)
    pager.add_page(
        demo_survey_page, "Conclusion",
        on_next=lambda _, p: conclude_session(p.get_data())
    )

    end_frame = WidgetFrame(root, pager.notebook)
    ttk.Label(end_frame, text="Thanks for Participating!").pack()
    ttk.Button(end_frame, text="Quit", command=lambda: sys.exit(0)).pack()
    pager.add_page(end_frame, "Thanks for participating")

    pager.select_page(0)

    root.set_frame(pager)
    root.raise_window()


# heavy function. run on thread
def setup_data(log: Callable[[str], None]):
    log('loading')
    cfg.load_from_file()

    log('connecting to database')
    global db
    db = firebase.init_db()
    log('loading')
    cfg.load_from_fb(db)

    return


# heavy function. run on thread
def setup_user_session(uuid: str, email: Optional[str], log: Callable[[str], None]) -> SurveySession:
    log('building survey')
    session = SurveySession(db=db, user_id=uuid, user_email=email)

    session.save_accept_terms()
    session.save_session_id_uuid_association()

    return session


# heavy function. run on thread
def setup_watermark(uuid: str, log: Callable[[str], None]) -> Watermark:
    log("setting up marks")
    m: list[Watermark] = []
    for am in active_watermarks().items(): m.append(am)

    # log("randomizing")
    # setup watermark randomizer with user as seed
    wm_rand = random.Random()
    wm_rand.seed(uuid)
    wm = wm_rand.choice(m)

    (name, _) = wm
    print(name)

    # todo: replace with mapping of wm->setup function | None
    if name == "wtgb":
        log('building models (this can take up to a few minutes)')
        wtgb.init_model()

    return wm


class AP(WidgetFrame):
    def _create_widgets(self):
        super()._create_widgets()
        self.ap = AuthPage(self.app, self)
        self.ap.pack()
        self.ap.on_login = self.on_login

        self.lw = LoadingWidget(self.app, self)
        self.lw.load = lambda kwargs: self.setup(**kwargs)
        self.lw.on_complete = lambda res: start_survey_ui(**res)

        self.lw.pack()
        # hide loader widget until used
        self.lw.pack_forget()

    def on_login(self, uuid, email):
        print(f"user {email} {uuid} login")

        # start loading
        config_enable(self, False)
        config_enable(self.lw, True)
        self.lw.pack()
        self.lw.start(uuid=uuid, email=email)

    def setup(self, uuid, email):
        print("starting setup")
        log = self.lw.post_progress
        session = setup_user_session(uuid, email, log)
        wm = setup_watermark(uuid, log)
        print("setup complete")

        return {'session': session, 'wm': wm}


def start_user_ui():
    auth_page = AP(root)

    terms_frame = TermsPage(root)
    terms_frame.on_accepted = lambda: root.set_frame(auth_page)

    root.set_frame(terms_frame)


if __name__ == "__main__":
    system("title " + "Study: Identification of AI-Generated Academic Texts Using Watermarks")
    print("Starting App...")

    root = App()

    splash_frame = WidgetFrame(root)
    splash_frame.pack()
    lw = splash_frame.lw = LoadingWidget(root, splash_frame)
    lw.load = lambda _: setup_data(lambda a, l=lw: l.post_progress(a))
    lw.pack()
    lw.on_complete = lambda _: start_user_ui()
    lw.start()

    root.set_frame(splash_frame)
    root.raise_window()

    root.mainloop()  # blocking call

    print("Bye!")
