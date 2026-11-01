# ClickHouseGNN

A graph machine learning project for financial transaction networks. ClickHouse and MLflow run with Docker Compose; ingestion, feature engineering, and model training are planned.

## Setup

Install [uv](https://docs.astral.sh/uv/) and Docker Compose, then run:

```sh
uv sync                       # Python 3.12 environment
cp .env.example .env          # First time only; set your password in .env
docker compose up -d
```

On macOS, PyTorch uses the standard macOS build. CPU is available, and MPS may be available for Apple GPU acceleration.

## Services

- ClickHouse: [SQL interface](http://localhost:8123/play), HTTP port `8123`, native port `9000`. Log in with the credentials in `.env`.
- MLflow: [http://localhost:5000](http://localhost:5000). Set `MLFLOW_TRACKING_URI=http://localhost:5000` for training clients.

Both services bind to localhost. Their data is stored in `data/clickhouse` and `data/mlflow`, which Git ignores. MLflow uses SQLite for metadata and stores artifacts locally.

Run `docker compose down` to stop the services without deleting data. Changing `.env` after ClickHouse initializes does not update its existing user. Run Python with `uv run python` and tests with `uv run pytest`.

## Planned workflow

Ingest transactions, compute historical graph features without future-data leakage, train GraphSAGE and a non-graph baseline, track experiments in MLflow, and evaluate precision, recall, F1, PR-AUC, and feature computation performance.
