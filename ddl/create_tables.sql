CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT,
    email         TEXT,
    country       TEXT,
    created_at    TIMESTAMP
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    name          TEXT,
    category      TEXT,
    price         NUMERIC(10, 2)
);

CREATE TABLE orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER,
    created_at    TIMESTAMP,
    status        TEXT
);

CREATE TABLE payments (
    payment_id    INTEGER PRIMARY KEY,
    order_id      INTEGER REFERENCES orders(order_id),
    amount        NUMERIC(10, 2),
    paid_at       TIMESTAMP,
    method        TEXT
);

CREATE TABLE events (
    event_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER,
    event_type    TEXT,
    happened_at   TIMESTAMP
);

CREATE TABLE fact_orders (
    order_id      INTEGER,
    customer_id   INTEGER,
    product_id    INTEGER,
    payment_id    INTEGER,
    amount        NUMERIC(10, 2),
    ordered_at    TIMESTAMP
);