# IMDb DB

Your local IMDb Database.

## Core Functionality

- Import the datasets from [imdb](https://datasets.imdbws.com/).
- Index into Postgres.
- Serve through a small API layer.
- Built with Python and FastAPI.

## Included Datasets

All datasets are imported from official IMDb sources. They are provided by imdb for local private personal and non-commercial use. For more details see [here](https://developer.imdb.com/non-commercial-datasets/).

| Name                  | Comment                       | Count | Size Compressed | Size raw | Size indexed | Ingest  | Upsert  |
|-----------------------|-------------------------------|-------|-----------------|----------|--------------|---------|---------|
| title.basics.tsv      | All titles                    |
| name.basics.tsv       | All names of people           |
| title.ratings.tsv     | All ratings of titles         |
| title.episode.tsv     | Episode to season mappings    |
| title.akas.tsv        | Alternative names for titles  |
| title.principals.tsv  | People to title relations     |

You don't have to import all datasets. But make sure the relations can be established, e.g. importing the title.akas dataset without the title.basics dataset would not make sense.

## Installation

This project depends on two containers: Postgres for the DB and the python container for the API. See the sample [compose file](https://github.com/bbilly1/imdb-db/blob/develop/docker-compose.yml) to get  started.

### Postgres

- The sample healthcheck is recommended for proper startup check of the API container.
- The command extension configuring the WAL is recommended for more efficient bulk data merging. You can adjust these values should you be limited on disk space.

Environment variables are the standard postgres vars:

```
POSTGRES_USER=imdb-db
POSTGRES_PASSWORD=secret123
POSTGRES_DB=imdb-db
```

### API

The API container can run under your own user by adding for example `user: 1000:1000`. If you do that, make sure to also set the volume permissions correctly.

- Interface is served on port 8000.
- Expects a volume at `/data` in the container. This is where the downloaded datasets go and where the decompressed files are stored. Clean periodically. 

For env vars, you'll need to provide both sync and async connection strings to postgres. E.g.:

```
DATABASE_URL=postgresql+asyncpg://imdb-db:secret123@imdb-postgres:5432/imdb-db
DATABASE_URL_SYNC=postgresql://imdb-db:secret123@imdb-postgres:5432/imdb-db
```

## Endpoints

The docs are available at `/docs` or at `/openapi.json`.

Available endpoints:

- `GET /api`
- `POST /api/ingest`
- `GET /api/import-tasks`
- `GET /api/stats`
- `GET /api/titles`
- `GET /api/titles/{tconst}`
- `GET /api/titles/{tconst}/principals`
- `GET /api/people/{nconst}`
- `GET /api/people/{nconst}/credits`
- `GET /api/series/{tconst}/episodes`
- `GET /api/search/titles`
- `GET /api/search/people`

## Ingest Dataset

In general, that works as such:

- Download the compressed *.tsv.gz file directly from imdb, store it in the cache folder
- Decompress the archive to *.tsv file in the cache folder
- Import the raw data into a temporary postgres staging table
- Upsert the staging table into the main table

Some testing has shown this approach to be the fastest, as that skips the ORM altogether, and all processing can be done directly in postgres. The main bottleneck will be IO on postgres during the COPY and INSERT commands.

### Trigger ingest for all datasets

```bash
curl -X POST /api/ingest
```

### Trigger ingest for selected datasets

```bash
curl -X POST /api/ingest \
  -H "Content-Type: application/json" \
  -d '{"data_set":["title.basics.tsv","title.ratings.tsv"]}'
```

### CLI

There is a small CLI utility included to trigger the ingest flows:

```
docker compose exec -it imdb-api ./backend/app/cli --help
```

## Local Development

You can run Postgres in Docker and API locally:

```bash
docker compose up -d imdb-postgres
source .venv/bin/activate
pip install -r requirements-dev.txt
cd backend/app
fastapi dev main.py
```

`devstart.sh` also provides a tmux-based local dev workflow.

## CI/CD Images

GitHub Actions builds and publishes multi-arch images to GHCR:
- `unstable` for `master` pushes
- release tag images for GitHub releases

Build metadata is exposed by API using:
- `GIT_TAG`
- `GIT_COMMIT`

## Security Notes

- There is no authentication on the API. Use only in trusted environments.
