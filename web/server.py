from contextlib import asynccontextmanager
from threading import Thread
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response

from services import wtgb
from watermarks import active_watermarks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("init wtgb model")
    wtgb.init_model()
    print("init wtgb done")

    yield  # app runs here

    # shutdown (optional cleanup)
    print("shutting down server")


app = FastAPI(lifespan=lifespan)

jobs = {}


def watermark_worker(job_id: str):
    try:
        print(f"{job_id}: running worker", end='')
        job = jobs[job_id]
        wm_name, text = job["wm"], job["text"]
        print(f" ({wm_name})")

        job["status"] = "running"

        m = active_watermarks()[wm_name]
        result = m(text)

        print(f"{job_id}: completed")
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        print(f"{job_id}: failed\n{e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/watermark", status_code=202)
def watermark(data: dict, request: Request, response: Response):
    print("client posted watermarking request:")

    job_id = str(uuid4())
    print(f"starting watermark job {job_id}")
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "result": None,
    }
    print(f"starting worker for wm job {job_id}")
    Thread(
        target=watermark_worker,
        args=(job_id, data["text"], data["wm"]),
        daemon=True
    ).start()

    print(f"{job_id}: job started")

    job_location = f"{str(request.base_url)}watermark/{job_id}"
    response.headers["Location"] = job_location

    return {
        "job_id": job_id,
        "status": "pending"
    }


@app.get("/watermark/{job_id}")
def get_watermark(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]
