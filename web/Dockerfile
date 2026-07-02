FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install torch==1.13.1 torchvision==0.14.1

RUN pip install git+https://github.com/JunnYu/WoBERT_pytorch.git

COPY web/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader \
    punkt \
    stopwords \
    averaged_perceptron_tagger

COPY Text_Watermark/ /app/Text_Watermark/
COPY services/ /app/services/
COPY watermark /app/watermark
COPY data/ /app/data/
COPY web/ /app/web/
COPY config.py /app/config.py


EXPOSE 8000

# Start server
CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]