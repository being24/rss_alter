FROM python:3.12-slim

WORKDIR /opt/

# set environment variables
ENV LC_CTYPE='C.UTF-8'
ENV TZ='Asia/Tokyo'
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG BOT_NAME="rss"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./ ${BOT_NAME}

RUN set -x && \
    apt-get update && \
    apt-get install --no-install-recommends -y build-essential nano git tzdata ncdu && \
    rm -rf /var/lib/apt/lists/* && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    cd ${BOT_NAME} && \
    uv sync --locked && \
    echo "Hello, ${BOT_NAME} ready!"


CMD ["/opt/rss/.venv/bin/python3","/opt/rss/src/main.py"]
