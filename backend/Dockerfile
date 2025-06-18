FROM python:3.13-alpine

RUN apk update && apk add curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:/app/.venv/bin/:$PATH"

ADD . /app

WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "main.py"]