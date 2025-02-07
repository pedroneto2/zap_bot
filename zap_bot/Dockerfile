FROM python:3.13.1-slim-bullseye

COPY ./docker-entrypoint.sh /

COPY . /app/zap_bot

RUN chmod +x /docker-entrypoint.sh && groupadd -r -g 1001 apps && useradd -r -u 1001 -g 1001 -s /bin/bash -m -d /app apps && chown -R apps.apps /app && \
    echo 'apps ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

WORKDIR /app/zap_bot
