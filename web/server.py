from threading import Thread
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from watermarks import active_watermarks

app = FastAPI()

jobs = {}


def watermark_worker(job_id: str, text: str, wm_name: str):
    try:
        print(f"{job_id}: running ({wm_name})")
        jobs[job_id]["status"] = "running"

        m = active_watermarks()[wm_name]
        result = m(text)

        print(f"{job_id}: completed")
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        print(f"{job_id}: failed\n{e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/watermark")
def watermark(data: dict):
    print("client posted watermarking request:")

    job_id = str(uuid4())
    print(f"starting wm job {job_id}")
    Thread(
        target=watermark_worker,
        args=(job_id, data["text"], data["wm"]),
        daemon=True
    ).start()

    print(f"{job_id}: job started")

    return {
        "job_id": job_id,
        "status": "pending"
    }

@app.get("/watermark/{job_id}")
def get_watermark(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]

print("hi server")