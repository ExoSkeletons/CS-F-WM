import os
import random
import sys
from datetime import datetime
from os import system
from tkinter.font import Font
from typing import Callable, Optional

import ttkbootstrap as ttk
from google.cloud.firestore_v1 import Client

from ui.theme import configure_style, Fonts
from ui.widgets.loading import LoadingWidget

# patch console out to devnull to avoid crashing logging if no console is attached
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import certifi

import config as cfg
from services import firebase
from services.generation import threaded_generation
from web.client import server_poll_watermarks
# from services import wtgb
# from watermark.watermarks import active_watermarks
from watermark.types import Watermark
from ui.app import App, WidgetFrame, config_enable, HeaderWidget
from config import data_dir_path
from ui.auth import TermsPage, AuthPage
from ui.demo import DemoPage
from ui.detect import DetectPage
from ui.survey import PagedFrame, SurveySession

os.environ["SSL_CERT_FILE"] = certifi.where()


def threaded_query(q: str, response_callback: Callable[[str, bool], None]):
    # update UI safely from main thread
    threaded_generation(q, lambda resp, ok: root.after(0, lambda r=resp, o=ok: response_callback(r, o)))


root: App
db: Client


def start_survey_ui(session: SurveySession, wm: Watermark):
    frame = WidgetFrame(root)
    header = HeaderWidget(root, "logo.png", ['jct.png', 'ariel.png', 'csic.png'], master=frame)
    header.pack(expand=True, fill="x")
    pager = PagedFrame(root, master=frame, next_text="Confirm", allow_tab_navigation=False, allow_prev=False)
    pager.pack(expand=True, fill="both")

    intro_frame = WidgetFrame(root, master=pager.notebook)
    intro_text = ""
    try:
        with open(data_dir_path + "introduction.txt", "rt", encoding='utf-8') as f:
            intro_text = f.read()
    except OSError as e:
        print(e)
        input("Could not load instructions.")
        exit(1)

    (ttk.Label(intro_frame, text="Introduction & Instructions", font=Fonts.h1)
     .pack(anchor="center"))
    (ttk.Label(intro_frame, text=intro_text, font=Font(font=Fonts.body, slant='italic'), wraplength=700)
     .pack(anchor="center"))
    pager.add_page(intro_frame, "Introduction")

    try:
        with open(data_dir_path + "questions.txt", "rt", encoding='utf-8') as f:
            questions: list[str] = f.readlines()
    except OSError as e:
        print(e)
        input("Could not load questions.")
        exit(1)

    # todo:
    # snapshot = db.collection('data').document('questions').get()
    # if not snapshot or not snapshot.exists:
    #     print(f"Failed to get questions document snapshot.\n{snapshot}.")
    #     return
    # questions = snapshot.to_dict()['list']

    page_amount = 4
    wm_amount = 2
    lf = [False for _ in range(page_amount - wm_amount)]
    lt = [True for _ in range(wm_amount)]
    flags = list(lf + lt)
    random.shuffle(flags)
    for i in range(page_amount):
        detect_page = DetectPage(
            root, master=pager.notebook,
            title=f"Assignment {i + 1}",
            watermark=wm, mark_prob=1.0 if flags[i] else 0.0,
            questions=questions
        )
        detect_page.on_submit = lambda q, page=detect_page: threaded_query(q.strip(), page.response)
        pager.add_page(
            detect_page, title=detect_page.title,
            validator=detect_page.resp_frame.is_valid,
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

    demo_survey_page = DemoPage(root, master=pager.notebook)
    pager.add_page(
        demo_survey_page, "",
        on_next=lambda _, p: conclude_session(p.get_data())
    )

    end_frame = WidgetFrame(root, master=pager.notebook)
    ttk.Label(end_frame, text="Thanks for participating").pack()
    ttk.Button(end_frame, text="Quit", command=lambda: sys.exit(0)).pack()
    pager.add_page(end_frame, "")

    pager.select_page(0)

    root.set_frame(frame, grow=True)
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

    # local watermarking
    # for am in active_watermarks().items(): m.append(am)

    # server based watermarking
    for am in server_poll_watermarks().items(): m.append(am)

    # log("randomizing")
    # setup watermark randomizer with user as seed
    wm_rand = random.Random()
    wm_rand.seed(uuid)
    wm = wm_rand.choice(m)

    (name, _) = wm
    print(name)

    # init local model for local watermarking
    # todo: replace with mapping of wm->setup function | None
    # if name == "wtgb":
    #    log('building models (this can take up to a few minutes)')
    #    wtgb.init_model()

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
    title = "Identification of AI-Generated Academic Texts Using Watermarks"
    system("title " + title)
    print("Starting App...")

    root = App(title=title, themename="litera")

    splash_frame = WidgetFrame(root)
    lw = splash_frame.lw = LoadingWidget(root, splash_frame)
    lw.load = lambda _: setup_data(lambda a, l=lw: l.post_progress(a))
    lw.pack()
    lw.on_complete = lambda _: start_user_ui()
    lw.start()

    root.set_frame(splash_frame)
    root.raise_window()

    configure_style()

    root.mainloop()  # blocking call

    print("Bye!")
