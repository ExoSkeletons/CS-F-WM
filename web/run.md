

Build

```
docker build -t watermark-api .
```

---

CPU mode

```
docker run -d \
  -p 8000:8000 \
  --restart unless-stopped \
  watermark-api
```

GPU mode

```
docker run -d \
  --gpus all \
  -p 8000:8000 \
  --restart unless-stopped \
  --name watermark-api \
  watermark-api
```
