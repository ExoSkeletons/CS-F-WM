import json
import threading
from typing import Callable, Any

import requests
from requests import HTTPError, ConnectionError
from tenacity import stop_after_attempt, wait_exponential_jitter, retry_if_exception_message, retry

from config import config


def fetch_models(key: str):
    res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
    res.raise_for_status()

    models = [m['name'] for m in res.json().get('models', []) if
              'generateContent' in m.get('supportedGenerationMethods', [])]
    return models


def google_generation(prompt: str) -> str:
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
    stop=stop_after_attempt(6),
    wait=wait_exponential_jitter(initial=0.5, max=4, jitter=0.5),
    retry=retry_if_exception_message(match=r"overloaded|503|500"),
    reraise=True,
)
def stubborn_generation(q: str) -> str:
    return google_generation(q)


def threaded_generation(q: str, response_callback: Callable[[str, bool], Any]):
    def worker():
        name = "AI Model" # config.get('model', {}).get('name', None)
        try:
            print(f"querying:\n\"{q}\"")
            resp = stubborn_generation(q)
            print(f"response OK. generated:\n\"{resp}\"")
            ok = True
        except Exception as e:
            resp = (
                    (
                        f"Could not connect to {name}. Is your internet ok?" if isinstance(e, ConnectionError) else
                        (
                            f"{name} is currently unavailable. ({e.response.reason})\n"
                            f"\n{dict(json.loads(e.response.text)).get('error', {}).get('message', '-')}"
                        ) if isinstance(e, HTTPError) else
                        f"Error Generating response."
                    ) + "\n"
                    # + "\nPlease try again later.\n"
                    + f"\n{e.__repr__()}"
            )
            ok = False
        response_callback(resp, ok)

    # run worker in background so UI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()
