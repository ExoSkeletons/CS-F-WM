FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    git \
    curl \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY web/requirements.txt /app/requirements.txt

RUN pip install torch==1.11.0+cpu torchvision==0.12.0+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

RUN pip install -r requirements.txt

RUN pip install git+https://github.com/JunnYu/WoBERT_pytorch.git

RUN python -m spacy download en_core_web_sm

COPY . /app

EXPOSE 8000

# Start server
CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]