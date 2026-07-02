import datetime
import time

import requests

from watermark.typing import Watermarks

SERVER_IP = "44.201.81.4"
SERVER_PORT = 8000

BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"


def submit_job(text: str, wm: str):
    endpoint_url = f"{BASE_URL}/watermark"

    payload = {
        "text": text,
        "wm": wm
    }
    res = requests.post(endpoint_url, json=payload)
    res.raise_for_status()

    data = res.json()
    job_id = data["job_id"]
    location = res.headers.get("Location")

    print(f"[submitted] job_id={job_id}")
    print(f"[location] {location}")

    return job_id, location


def poll_job(job_url: str, interval: float = 0.5, timeout: int = 300):
    start = time.time()

    last_status = None
    while True:
        res = requests.get(job_url)

        if res.status_code == 404:
            raise RuntimeError("Job not found (server restarted?)")

        data = res.json()
        status = data.get("status")

        if last_status != status:
            if last_status is not None: print()
            print(f"[{datetime.datetime.now()}][status] {status}", end="")
        else:
            print(".", end="")
        last_status = status

        if status == "completed":
            print(f"[{datetime.datetime.now()}][status] completed")
            return data["result"]

        if status == "failed":
            raise RuntimeError(f"Job failed: {data.get('error')}")

        if time.time() - start > timeout:
            raise TimeoutError("Job polling timed out")

        time.sleep(interval)


def request_wm_and_await(text: str, wm: str):
    job_id, location = submit_job(text, wm)
    print(f"[submitted] job_id={job_id}")
    print(f"[location] {location}")
    # todo: interval etc. from config
    res = poll_job(job_id, interval=1, timeout=600)
    return res


def server_poll_watermarks() -> Watermarks:
    # todo: load from config/fb
    wm_names = ['space-replace', 'acrostic', 'wtgb']
    return {
        wm_name: lambda t: request_wm_and_await(text=t, wm=wm_name)
        for wm_name in wm_names
    }


if __name__ == "__main__":
    text = "This is a test sentence to be watermarked by the server." * 10

    wm_tests = ['upper', 'phishing', 'space-replace', 'acrostic', 'wtgb']

    print("\n=== WATERMARKS ===\n")
    for wm in wm_tests:
        print(f"--- {wm} ---\n")

        print("Submitting job...", end='')
        job_id, job_location = submit_job(text, wm)
        print(f"Done. Awaiting job [{job_id}] Result...", end='')
        result = poll_job(job_location)
        print(f"Done.")

        print("\n--- Result ---")
        print(result)
        print()
