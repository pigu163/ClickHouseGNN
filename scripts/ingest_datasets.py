"""Load the HI-Small and LI-Small CSV files into ClickHouse.

The script applies ``sql/schema.sql`` and then replaces the contents of the
four dataset tables. It inserts CSV rows in bounded batches rather than
loading each full file into memory.
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import clickhouse_connect

ROOT = Path(__file__).resolve().parents[1]
TRANSACTION_COLUMNS = [
    "event_time",
    "from_bank",
    "from_account",
    "to_bank",
    "to_account",
    "amount_received",
    "receiving_currency",
    "amount_paid",
    "payment_currency",
    "payment_format",
    "is_laundering",
]
ACCOUNT_COLUMNS = ["bank_name", "bank_id", "account_number", "entity_id", "entity_name"]
# The transaction CSV has two columns named "Account". csv.reader preserves
# their positions: column 3 is the sender account and column 5 is the receiver.
# Keep the positional header intact, then map those values to distinct DB columns.
TRANSACTION_HEADER = [
    "Timestamp",
    "From Bank",
    "Account",
    "To Bank",
    "Account",
    "Amount Received",
    "Receiving Currency",
    "Amount Paid",
    "Payment Currency",
    "Payment Format",
    "Is Laundering",
]
ACCOUNT_HEADER = ["Bank Name", "Bank ID", "Account Number", "Entity ID", "Entity Name"]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def insert_csv(client, path: Path, table: str, kind: str, batch_size: int) -> int:
    """Validate and insert one CSV, converting transaction values as needed.

    Returns the number of rows inserted into ``table``.
    """
    expected_header = TRANSACTION_HEADER if kind == "transactions" else ACCOUNT_HEADER
    columns = TRANSACTION_COLUMNS if kind == "transactions" else ACCOUNT_COLUMNS
    batch: list[tuple] = []
    inserted = 0
    started = time.monotonic()

    with path.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.reader(source)
        header = next(reader, None)
        if header != expected_header:
            raise ValueError(f"Unexpected header in {path}: {header!r}")

        for row_number, row in enumerate(reader, start=2):
            if len(row) != len(columns):
                raise ValueError(f"{path}:{row_number}: expected {len(columns)} columns, got {len(row)}")
            if kind == "transactions":
                values = (
                    # Source timestamps have no timezone. Treat them as UTC so
                    # the host's local timezone cannot silently shift event times.
                    datetime.strptime(row[0], "%Y/%m/%d %H:%M").replace(tzinfo=timezone.utc),
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    # Decimal preserves the source's exact decimal amount digits;
                    # binary float can introduce rounding before values reach ClickHouse.
                    Decimal(row[5]),
                    row[6],
                    Decimal(row[7]),
                    row[8],
                    row[9],
                    int(row[10]),
                )
            else:
                values = tuple(row)
            batch.append(values)

            # Flush bounded batches so multi-gigabyte CSV files are not held in
            # memory at once; the batch size also controls each insert request.
            if len(batch) >= batch_size:
                client.insert(table, batch, column_names=columns)
                inserted += len(batch)
                batch.clear()
                print(f"{table}: {inserted:,} rows", flush=True)

        if batch:
            client.insert(table, batch, column_names=columns)
            inserted += len(batch)

    elapsed = time.monotonic() - started
    print(f"{table}: complete, {inserted:,} rows in {elapsed:.1f}s", flush=True)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=ROOT / "dataset")
    parser.add_argument("--schema", type=Path, default=ROOT / "sql" / "schema.sql")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--batch-size", type=int, default=50_000)
    args = parser.parse_args()

    # Prefer the user's local .env; use .env.example on a fresh checkout that
    # does not have a local configuration file yet.
    if not args.env_file.exists() and (ROOT / ".env.example").exists():
        args.env_file = ROOT / ".env.example"
    load_env_file(args.env_file)

    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "app"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "local-dev-password"),
        database=os.getenv("CLICKHOUSE_DB", "transactions"),
    )
    # Apply the table definitions before loading data. IF NOT EXISTS creates
    # missing tables, but it does not migrate the schema of tables already there.
    for statement in args.schema.read_text(encoding="utf-8").split(";"):
        if statement.strip():
            client.command(statement)

    # These tables are dedicated to the two source datasets. Clearing them first
    # makes a rerun replace old or partial data instead of appending duplicates.
    for table in ("hi_transactions", "hi_accounts", "li_transactions", "li_accounts"):
        client.command(f"TRUNCATE TABLE {table}")

    totals = {}
    for dataset in ("HI-Small", "LI-Small"):
        # Keep HI and LI rows in separate transaction and account tables.
        prefix = "hi" if dataset.startswith("HI") else "li"
        directory = args.dataset_dir / dataset
        totals[f"{prefix}_transactions"] = insert_csv(
            client,
            directory / f"{dataset}_Trans.csv",
            f"{prefix}_transactions",
            "transactions",
            args.batch_size,
        )
        totals[f"{prefix}_accounts"] = insert_csv(
            client,
            directory / f"{dataset}_accounts.csv",
            f"{prefix}_accounts",
            "accounts",
            args.batch_size,
        )
    client.close()
    print("Imported row totals:")
    for table, count in totals.items():
        print(f"  {table}: {count:,}")


if __name__ == "__main__":
    main()
