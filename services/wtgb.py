from datetime import datetime
from typing import Optional

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
    if do_post_process: wm_text = post_process(wm_text)
    tw = datetime.now()

    print(f'wm done. took {tw - tw0}s')

    return wm_text


def post_process(wm_text: str) -> str:
    return (
        wm_text
        .replace(' .', '.')
        .replace(' ,', ',')
        .replace(' ;', ',')
        .replace(' \' s ', '\'s ')
        .replace(' \'', '\'')
    )
