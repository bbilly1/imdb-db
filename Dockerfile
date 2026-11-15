FROM node:24 AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json /frontend/
RUN npm ci

COPY frontend/index.html /frontend/index.html
COPY frontend/src /frontend/src
COPY frontend/tsconfig.json frontend/tsconfig.node.json /frontend/
COPY frontend/vite.config.ts frontend/tailwind.config.ts /frontend/

RUN npm run build

FROM python:3.14.8-slim-trixie

ARG TARGETARCH
ARG GIT_COMMIT=unknown
ARG GIT_TAG=0.0.1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CACHE_DIR=/data/cache \
    FRONTEND_DIST=/app/frontend-dist

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini curl ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN case "$TARGETARCH" in \
        amd64) checksum=1692066e350a88ff4d7d6474fe3c7a6c41ec5e89 ;; \
        arm64) checksum=9d4c2000493215a1898502b2fc2dada3e8ea8c7a ;; \
        *) echo "Unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac \
    && curl -fsSL "https://github.com/aptible/supercronic/releases/download/v0.2.51/supercronic-linux-${TARGETARCH}" -o /usr/local/bin/supercronic \
    && echo "$checksum  /usr/local/bin/supercronic" | sha1sum -c - \
    && chmod +x /usr/local/bin/supercronic

RUN python -m venv /applib
ENV PATH="/applib/bin:$PATH"

WORKDIR /app

COPY backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY backend /app/backend
COPY --from=frontend-builder /frontend/dist /app/frontend-dist
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

ENV GIT_COMMIT=${GIT_COMMIT} \
    GIT_TAG=${GIT_TAG}

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "-g", "--"]
CMD ["/app/run.sh"]
