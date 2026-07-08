from contextlib import asynccontextmanager
from threading import Thread
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response

import config
from config import max_len
from services import wtgb
from watermark.watermarks import marks

jobs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("sever starting")

    # init config
    print("loading config")
    config.load_from_file()  # todo: load fb

    # init model
    print("init wtgb model")
    wtgb.init_model()
    print("init wtgb done")

    yield  # app runs here

    # shutdown (optional cleanup)
    print("shutting down server")


app = FastAPI(lifespan=lifespan)


def watermark_worker(job_id: str):
    try:
        print(f"{job_id}: running worker", end='')
        job = jobs[job_id]
        wm_name, text = job["wm"], job["text"]
        print(f" ({wm_name})")

        job["status"] = "running"

        m = marks()[wm_name]
        result = m(text)

        print(f"{job_id}: completed")
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        print(f"{job_id}: failed\n{e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


max_len = {
    "wtgb": 50
}


@app.post("/watermark", status_code=202)
def watermark(data: dict, request: Request, response: Response):
    print(f"client posted watermarking request:\n{data}")

    wm_name = data["wm"]
    if wm_name not in marks().keys():
        print(f"wm {wm_name} not found")
        raise HTTPException(status_code=400, detail=f"watermark {wm_name} not found")

    if wm_name in max_len:
        text = data["text"]
        l = max_len[wm_name]
        if len(text) > l:
            raise HTTPException(
                status_code=401,
                detail=f"text too long.\n"
                       f"current server specs are low,"
                       f"watermarking with {wm_name} temporarily limited to {l} characters."
            )

    job_id = str(uuid4())
    print(f"starting watermark job {job_id}")
    jobs[job_id] = {
        "job_id": job_id,
        "wm": data["wm"],
        "text": data["text"],
        "status": "pending",
        "result": None,
    }
    print(f"starting worker for wm job {job_id}")
    try:
        Thread(
            target=watermark_worker,
            kwargs={'job_id': job_id},
            daemon=True
        ).start()
    except Exception as e:
        print(f"{job_id}: failed to start worker\n{e}")
        jobs[job_id]["status"] = "failed"

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
