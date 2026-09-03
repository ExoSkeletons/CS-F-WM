# Webserver Watermarking

For consistency and better compute one might opt to move the watermarking process to a Cloud-based remote server.

* `server.py`
  * FastAPI webserver.
  * Accepts wm requests. Returns the watermarker job. Watermark results are to be polled by polling the given job.
    * *See `submit_job`, `poll_job`, `request_wm_and_await`*
* `client.py`
  * Tester client
  * Supplies server polling watermarks
    * *See `server_poll_watermarks`*

---

# Configuration

*TODO*

# Deployment

We deployed our server on an AWS EC2 with Docker.

## Init Docker 

```shell
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

## Build

```shell
cd CS-F-WM
docker build -f ./web/Dockerfile -t watermark-api .
```

## Run

CPU mode

```shell
docker run -d \
  -p 8000:8000 \
  --restart unless-stopped \
  watermark-api
```

GPU mode

```shell
docker run -d \
  --gpus all \
  -p 8000:8000 \
  --restart unless-stopped \
  --name watermark-api \
  watermark-api
```
