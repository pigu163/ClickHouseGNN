# ClickHouseGNN

An end-to-end graph machine learning project for financial transaction networks and fraud detection. The planned pipeline uses ClickHouse for temporal graph features, PyTorch Geometric for model training, and MLflow for experiment tracking.

## Status

This repository is at the planning stage. The infrastructure, ingestion, feature queries, models, and evaluation pipeline have not yet been implemented. Setup and usage instructions will be added as those components become available.

## Planned workflow

1. Ingest financial transactions into ClickHouse MergeTree tables.
2. Compute node and edge features over configurable historical windows, without using future transactions.
3. Build graphs with PyTorch Geometric and train a GraphSAGE model alongside a non-graph baseline.
4. Track dataset versions, feature configurations, models, and metrics in MLflow.
5. Evaluate precision, recall, F1, and PR-AUC, and benchmark feature computation.

The intended stack is Python 3.12+, SQL, uv, ClickHouse, PyTorch Geometric, MLflow, Polars, NumPy, PyArrow, Docker Compose, and pytest.
