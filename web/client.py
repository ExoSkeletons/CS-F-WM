import time
from urllib.error import HTTPError

import requests

SERVER_IP = "54.175.192.101"
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

    while True:
        res = requests.get(job_url)

        if res.status_code == 404:
            raise RuntimeError("Job not found (server restarted?)")

        data = res.json()
        status = data.get("status")

        print(f"[status] {status}")

        if status == "completed":
            return data["result"]

        if status == "failed":
            raise RuntimeError(f"Job failed: {data.get('error')}")

        if time.time() - start > timeout:
            raise TimeoutError("Job polling timed out")

        time.sleep(interval)


if __name__ == "__main__":
    text = "This is a test sentence to be watermarked by the server."

    wm_tests = ['upper', 'phishing', 'space-replace', 'acrostic', 'wtgb']

    print("\n=== WATERMARKS ===\n")
    for wm in wm_tests:
        print(f"--- {wm} ---\n")

        print("Submitting job...", end='')
        job_id, job_location = submit_job(text, wm)
        print(f"Done. Awaiting job [{job_id}] Result...", end='')
        result = poll_job(job_location)
        print(f"Done.")

        print("\n=== RESULT ===\n")
        print(result)
        print()