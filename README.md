# ClickHouseGNN

An end-to-end graph machine learning project for financial transaction networks and fraud detection. The planned pipeline uses ClickHouse for temporal graph features, PyTorch Geometric for model training, and MLflow for experiment tracking.

## Status

ClickHouse and MLflow are available through Docker Compose. Ingestion, feature queries, models, and evaluation have not yet been implemented.

## Start the services

Install Docker Desktop (or Docker Engine with Compose), then run:

```sh
cp .env.example .env
docker compose up -d
```

The copy command is only needed once; running it again overwrites `.env`. Set a local password in `.env` before starting. This file is ignored by Git; `.env.example` is the shared template.

ClickHouse listens on `localhost:8123` (HTTP) and `localhost:9000` (native). Open its SQL interface at [http://localhost:8123/play](http://localhost:8123/play) and use the credentials from `.env`. Try `SELECT 1;` or `SHOW TABLES FROM transactions;`.

MLflow is available at [http://localhost:5000](http://localhost:5000); set `MLFLOW_TRACKING_URI=http://localhost:5000` in training clients. Both services bind to localhost. Data is stored in `data/clickhouse` and `data/mlflow` under the project root; MLflow uses SQLite for tracking metadata and stores artifacts in the same directory. The `data/` directory is ignored by Git.

To stop the services without deleting their data, run `docker compose down`. Changing ClickHouse initialization credentials in `.env` after its data directory has been initialized does not update the existing user.

## Planned workflow

1. Ingest financial transactions into ClickHouse MergeTree tables.
2. Compute node and edge features over configurable historical windows, without using future transactions.
3. Build graphs with PyTorch Geometric and train a GraphSAGE model alongside a non-graph baseline.
4. Track dataset versions, feature configurations, models, and metrics in MLflow.
5. Evaluate precision, recall, F1, and PR-AUC, and benchmark feature computation.

The intended stack is Python 3.12+, SQL, uv, ClickHouse, PyTorch Geometric, MLflow, Polars, NumPy, PyArrow, Docker Compose, and pytest.
