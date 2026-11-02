CREATE TABLE IF NOT EXISTS hi_transactions
(
    event_time DateTime64(0, 'UTC'),
    from_bank String,
    from_account String,
    to_bank String,
    to_account String,
    amount_received Decimal(20, 6),
    receiving_currency LowCardinality(String),
    amount_paid Decimal(20, 6),
    payment_currency LowCardinality(String),
    payment_format LowCardinality(String),
    is_laundering UInt8
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, from_bank, from_account, to_bank, to_account);

CREATE TABLE IF NOT EXISTS hi_accounts
(
    bank_name String,
    bank_id String,
    account_number String,
    entity_id String,
    entity_name String
)
ENGINE = MergeTree
ORDER BY (bank_id, account_number);

CREATE TABLE IF NOT EXISTS li_transactions
(
    event_time DateTime64(0, 'UTC'),
    from_bank String,
    from_account String,
    to_bank String,
    to_account String,
    amount_received Decimal(20, 6),
    receiving_currency LowCardinality(String),
    amount_paid Decimal(20, 6),
    payment_currency LowCardinality(String),
    payment_format LowCardinality(String),
    is_laundering UInt8
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, from_bank, from_account, to_bank, to_account);

CREATE TABLE IF NOT EXISTS li_accounts
(
    bank_name String,
    bank_id String,
    account_number String,
    entity_id String,
    entity_name String
)
ENGINE = MergeTree
ORDER BY (bank_id, account_number);
