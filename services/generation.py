import threading
from typing import Callable, Any

import requests
from tenacity import retry, stop_after_delay, wait_exponential_jitter, retry_if_exception_message, RetryError

from config import config


def generation(q: str) -> str:
    model = config['model']
    key = config['genai_api_key']

    # had to downgrade from this to direct http request, due to versions
    # return client.models.generate_content(model=model, contents=q).text

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": key}

    data = {
        "contents": [
            {"parts": [{"text": q}]}
        ]
    }

    res = requests.post(url, headers=headers, params=params, json=data)
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
    stop=stop_after_delay(max_delay=10),
    wait=wait_exponential_jitter(initial=0.5, max=10),
    retry=retry_if_exception_message(match=r"overloaded|503"),
)
def stubborn_generation(q: str) -> str:
    print(f"querying:\n\"{q}\"")
    return generation(q)


def threaded_generation(q: str, response_callback: Callable[[str, bool], Any]):
    def worker():
        try:
            resp = stubborn_generation(q)
            ok = True
        except RetryError as e:
            resp = (f"Retry Timed out, Could not reach Text Generation services ({config['model']}).\n"
                    "Is your Internet OK?\n"
                    f"{e.__repr__()}"
                    )
            ok = False
        except Exception as e:
            resp = f"Error Generating response.\n{e.__repr__()}"
            ok = False
        response_callback(resp, ok)

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()
