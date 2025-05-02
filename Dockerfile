FROM python:3.12-alpine

WORKDIR /opt/

# set environment variables
ENV LC_CTYPE='C.UTF-8'
ENV TZ='Asia/Tokyo'
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG BOT_NAME="rss"

COPY ./ ${BOT_NAME}

RUN set -x && \
    apk add --no-cache build-base nano git tzdata ncdu && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    python3 -m pip install -U setuptools && \
    cd ${BOT_NAME} && \
    python3 -m pip install -r requirements.txt && \
    echo "Hello, ${BOT_NAME} ready!"


CMD ["python3","/opt/rss/src/main.py"]