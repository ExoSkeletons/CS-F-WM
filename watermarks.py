import random
from typing import Callable, Mapping, Union, Optional

from config import config
from services import wtgb
from services.generation import stubborn_generation

Marker = Callable[[str], str]
Detector = Callable[[str], float]

Watermark = tuple[str, Union[Marker, None, tuple[Marker, Optional[Detector]]]]
Watermarks = dict[str, Union[Marker, None, tuple[Marker, Optional[Detector]]]]


def marks() -> Watermarks:
    acrostic_config: dict[str, str] = config.get('acrostic', None)

    return {
        "upper": lambda s: s.upper(),
        "space#": lambda s: s.replace(' ', '#'),
        "ab": lambda s: s.replace('A', 'B').replace('a', 'b'),
        "phishing": lambda s: s.replace("m", "rn"),
        "wtgb": lambda s: wtgb.watermark(s),
        "space-replace": lambda s: s.replace(' ', random.choice(['\u2004', '\u2005', '\u2006', '\u2007', '\u2008'])),
        "acrostic": lambda s: s if not acrostic_config else stubborn_generation(
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
