# Base image (CUDA-ready)
FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# make python3.9 default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN pip install --upgrade pip

COPY web/requirements.txt /app/requirements.txt

RUN pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 \
    --extra-index-url https://download.pytorch.org/whl/cu113

RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=4

EXPOSE 8000

# Start server
CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]