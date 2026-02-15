# IMDb DB

Your local IMDb Database.

## Core Functionality

- Import the datasets from [imdb](https://datasets.imdbws.com/).
- Index into Postgres.
- Serve through a small API layer.
- Built with Python and FastAPI.

## Included Datasets

All datasets are imported from official IMDb sources. They are provided by imdb for local private personal and non-commercial use. For more details see [here](https://developer.imdb.com/non-commercial-datasets/).

| Name                  | Comment                       | Rows  | .tsv.gz | .tsv   | indexed | Ingest  | Upsert  |
|-----------------------|-------------------------------|-------|---------|--------|---------|---------|---------|
| title.basics.tsv      | All titles                    | 12 M  | 220 MB  | 1 GB   | 2 GB    | 1m 10s  |         |
| name.basics.tsv       | All names of people           | 15 M  | 300 MB  | 1 GB   | 2.4 GB  | 1m 40s  |         |
| title.ratings.tsv     | All ratings of titles         | 232 M | 10 MB   | 30 MB  | 220 MB  | 30s     |         |
| title.episode.tsv     | Episode to season mappings    | 10 M  | 50 MB   | 250 MB | 1.4 GB  | 5m      |         |
| title.akas.tsv        | Alternative names for titles  | 55 M  | 500 MB  | 2.7 GB | 12.6 GB | 17m     |         |
| title.principals.tsv  | People to title relations     | 98 M  | 750 MB  | 4.3 GB | 24 GB   | 1h      |         |

- Ingest and Upsert times are largely IO bound.
- These values are from local testing on consumer grade NVMe drives, YMMV.

You don't have to import all datasets. 
- Make sure the relations can be established, e.g. importing the `title.akas` dataset without the `title.basics` dataset would not make sense.
- You can do partial upserts, e.g. refresh only `title.ratings`. This will ignore titles for new ratings missing from `title.basics`. To avoid that, upsert `title.basics` and `title.ratings` together.

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
