FROM python:3.13.11-slim-trixie

ARG GIT_COMMIT=unknown
ARG GIT_TAG=0.0.1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CACHE_DIR=/data/cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /applib
ENV PATH="/applib/bin:$PATH"

WORKDIR /app

COPY backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY backend /app/backend
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

ENV GIT_COMMIT=${GIT_COMMIT} \
    GIT_TAG=${GIT_TAG}

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/run.sh"]
