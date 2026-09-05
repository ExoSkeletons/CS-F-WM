# Webserver Watermarking

For performance consistency and better compute when using heavy Watermarking, we built a simple webserver to process watermark requests remotely on the Cloud.

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

```json lines
{
  wm_server: {
    address: "xxx.xxx.xxx.xxx",
    port: 8000
  }
}
```

# Deployment

We deployed our server on an AWS EC2 with Docker.

## Init Docker 

```shell
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Be sure to `exit` and relog.

## Build

```shell
cd CS-F-WM
docker build -f ./web/Dockerfile -t wm-server .
```

## Run

CPU mode

```shell
docker run -d \
  -p 8000:8000 \
  --restart unless-stopped \
  wm-server
```

GPU mode

```shell
docker run -d \
  --gpus all \
  -p 8000:8000 \
  --restart unless-stopped \
  --name watermark-api \
  wm-server
```
