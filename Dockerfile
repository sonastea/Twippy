FROM python:3.10.6-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

ARG TOKEN
ENV TOKEN=${TOKEN}

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "twippy"]
