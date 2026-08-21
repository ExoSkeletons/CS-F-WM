import threading
from typing import Callable, Any

import requests
from requests import HTTPError
from tenacity import retry, stop_after_delay, wait_exponential_jitter, retry_if_exception_message, RetryError

from config import config


def fetch_models(key: str):
    res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
    res.raise_for_status()

    models = [m['name'] for m in res.json().get('models', []) if
              'generateContent' in m.get('supportedGenerationMethods', [])]
    return models


def generation(prompt: str) -> str:
    model_config = config['model']
    model = str(model_config['name'])
    temp = float(model_config.get('temperature', 1.0))

    key = config['genai_api_key']

    # had to downgrade from this to direct http request, due to versions
    # return client.models.generate_content(model=model, contents=q).text

    url = f"https://generativelanguage.googleapis.com/v1/interactions"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key,
    }
    data = {
        "model": model,
        "input": prompt,
        "generation_config": {
            "temperature": temp  # 0.0 to 2.0
        }
    }

    res = requests.post(url, headers=headers, json=data)
    try:
        res.raise_for_status()
    except HTTPError as e:
        if e.response:
            print(e.response.json())
        raise e

    d = dict(res.json())
    steps = d['steps']
    outputs = list(filter(lambda step: step['type'] == 'model_output', steps))
    contents = outputs[0]['content']
    texts = list(filter(lambda content: content['type'] == "text", contents))
    text = texts[0]['text']

    return text


@retry(
    stop=stop_after_delay(max_delay=10),
    wait=wait_exponential_jitter(initial=0.5, max=10),
    retry=retry_if_exception_message(match=r"overloaded|503|500"),
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
            resp = (f"{config['model']['name']} is currently experiencing high demand.\n"
                    "Please try again.\n"
                    )
            ok = False
        except Exception as e:
            resp = f"Error Generating response.\n{e.__repr__()}"
            ok = False
        response_callback(resp, ok)

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()
