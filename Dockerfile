FROM python:3.13.11-slim-trixie

ARG GIT_COMMIT=unknown
ARG GIT_TAG=0.0.1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CACHE_DIR=/data/cache \
    GIT_COMMIT=${GIT_COMMIT} \
    GIT_TAG=${GIT_TAG}

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/run.sh"]
