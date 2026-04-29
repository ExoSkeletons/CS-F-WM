import os
import re
import sys
from datetime import datetime
from typing import Optional

import spacy

MODEL_NAME = "en_core_web_sm"
MODEL_VERSION = "3.5.0"


def resolve_model_path():
    model_dir = f"{MODEL_NAME}-{MODEL_VERSION}"
    # PyInstaller onefile
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
        return os.path.join(base_path, MODEL_NAME, model_dir)

    # Dev environment (venv / site-packages)
    import en_core_web_sm
    pkg_path = os.path.dirname(en_core_web_sm.__file__)
    return os.path.join(pkg_path, model_dir)


MODEL_PATH = resolve_model_path()

_real_load = spacy.load


def patched_load(name, *args, **kwargs):
    if name == MODEL_NAME:
        return _real_load(MODEL_PATH, *args, **kwargs)
    return _real_load(name, *args, **kwargs)


spacy.load = patched_load

from Text_Watermark.models.watermark_faster import watermark_model

model: Optional[watermark_model] = None


def init_model():
    global model
    if model is not None: return
    # init
    print("init...")
    ti0 = datetime.now()
    print("-nltk")
    import nltk
    nltk.download('punkt')
    print("-model")
    model = watermark_model(language='English', mode='embed', tau_word=0.8, lamda=0.83)

    ti = datetime.now()
    print(f"init done. took {ti - ti0}s")


def watermark(ori_text: str, do_post_process: bool = True) -> str:
    # watermark
    global model
    print("watermarking...")
    tw0 = datetime.now()
    wm_text = model.embed(ori_text)
    if do_post_process: wm_text = fix_spacing(wm_text)
    tw = datetime.now()

    print(f'wm done. took {tw - tw0}s')

    return wm_text


def fix_spacing(text: str) -> str:
    # 1. Remove spaces before punctuation and closing brackets
    text = re.sub(r"\s+([,.;:!?)\]}])", r"\1", text)

    # 2. Remove spaces after opening brackets
    text = re.sub(r"([(\[{])\s+", r"\1", text)

    # 3. Fix contractions (supports ' and ’)
    text = re.sub(r"\b(\w+)\s+[\'’]\s+(\w+)\b", r"\1'\2", text)

    # 4. Fix hyphenated words
    text = re.sub(r"\b(\w+)\s+-\s+(\w+)\b", r"\1-\2", text)

    # 5. Remove padding inside quotes
    text = re.sub(r"([\"'])\s+([^\"']*?)\s+\1", r"\1\2\1", text)

    return text
