import datetime
import time

import requests
from requests import HTTPError

from config import config
from watermark.types import Watermarks


def submit_job(text: str, wm: str, ip: str, port: int = 8000):
    base_url = f"http://{ip}:{port}"
    endpoint_url = f"{base_url}/watermark"

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


def request_wm_and_await(text: str, wm: str, ip: str, port: int):
    job_id, location = submit_job(text=text, wm=wm, ip=ip, port=port)
    print(f"[submitted] job_id={job_id}")
    print(f"[location] {location}")
    # todo: interval etc. from config
    res = poll_job(job_id, interval=1, timeout=600)
    return res


def server_poll_watermarks() -> Watermarks:
    wm_names = ['space-replace', 'acrostic', 'wtgb']
    server_config = config["wm_server"]
    ip = str(server_config.get('ip', None) or server_config.get('address', None))
    port = int(server_config['port'])
    return {
        wm_name: lambda t, n=wm_name, i=ip, p=port: request_wm_and_await(text=t, wm=n, ip=i, port=p)
        for wm_name in wm_names
    }


if __name__ == "__main__":
    text = "This is a test sentence to be watermarked by the server." * 10

    wm_tests = ['upper', 'phishing', 'space-replace', 'acrostic', 'wtgb']

    print("\n=== WATERMARKS ===\n")
    for wm in wm_tests:
        print(f"--- {wm} ---\n")

        try:
            print("Submitting job...", end='')

            SERVER_IP = "3.83.31.129"
            SERVER_PORT = 8000

            job_id, job_location = submit_job(text, wm, SERVER_IP, SERVER_PORT)
            print(f"Done.\nAwaiting job [{job_id}]", end=' ')
            result = poll_job(job_location)
            print(f"Done.")

            print("\n--- Result ---")
            print(result)
            print()
        except Exception as e:
            if isinstance(e, TimeoutError):
                print(f"Timeout.\n{e}")
            elif isinstance(e, HTTPError):
                print(f"HTTPError.\n{e}")
                print(e.response.text)
            else:
                print(f"Error:\n{e}")
