FROM python:3.11.3-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

ARG TOKEN
ENV TOKEN=${TOKEN}

WORKDIR /app

COPY . .
RUN <<-EOF
    pip install --no-cache-dir --upgrade pip==23.1.2
    pip install --no-cache-dir .
EOF


CMD ["python", "twippy"]
