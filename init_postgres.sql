-- Initialize schema, tables, constraints, and indexes for the DWH practice dataset.
-- Run this once against your local Postgres before running ingest_postgres.py.

CREATE SCHEMA IF NOT EXISTS raw;

-- =========================================
-- Dimension: customers
-- =========================================

CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id            INTEGER PRIMARY KEY,
    first_name             TEXT,
    last_name              TEXT,
    email                  TEXT,
    phone_number           TEXT,
    registration_date      TIMESTAMP,
    customer_segment       TEXT,
    preferred_channel      TEXT,
    age_group              TEXT,
    income_level           TEXT,
    avg_order_value        NUMERIC,
    promo_sensitivity      NUMERIC,
    email_opt_in           BOOLEAN,
    sms_opt_in             BOOLEAN,
    push_opt_in            BOOLEAN,
    last_purchase_date     TIMESTAMP,
    total_lifetime_orders  INTEGER,
    preferred_category     TEXT
);

-- =========================================
-- Dimension: promotions
-- =========================================

CREATE TABLE IF NOT EXISTS raw.promotions (
    promotion_id           INTEGER PRIMARY KEY,
    campaign_name          TEXT,
    promo_type             TEXT,
    discount_value         NUMERIC,
    min_order_value        NUMERIC,
    start_date             TIMESTAMP,
    end_date               TIMESTAMP,
    campaign_duration_days INTEGER,
    target_segment         TEXT,
    campaign_channel       TEXT,
    campaign_objective     TEXT,
    target_category        TEXT,
    expected_response_rate NUMERIC,
    budget_allocated       NUMERIC,
    cost_per_acquisition   NUMERIC
);

-- =========================================
-- Fact: orders
-- =========================================

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id                 INTEGER PRIMARY KEY,
    customer_id              INTEGER NOT NULL,
    order_date               TIMESTAMP,
    order_status             TEXT,
    promotion_id             INTEGER,
    order_channel            TEXT,
    order_value              NUMERIC,
    attributed_to_promo      BOOLEAN,
    customer_segment_at_time TEXT,
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES raw.customers (customer_id),
    CONSTRAINT fk_orders_promotion
        FOREIGN KEY (promotion_id)
        REFERENCES raw.promotions (promotion_id)
);

-- =========================================
-- Fact: order_items
-- =========================================

CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id       INTEGER PRIMARY KEY,
    order_id            INTEGER NOT NULL,
    product_id          INTEGER,
    product_category    TEXT,
    quantity            INTEGER,
    unit_price          NUMERIC,
    promotion_id        INTEGER,
    attributed_to_promo BOOLEAN,
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES raw.orders (order_id),
    CONSTRAINT fk_order_items_promotion
        FOREIGN KEY (promotion_id)
        REFERENCES raw.promotions (promotion_id)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS ix_orders_customer_id
    ON raw.orders (customer_id);

CREATE INDEX IF NOT EXISTS ix_orders_promotion_id
    ON raw.orders (promotion_id);

CREATE INDEX IF NOT EXISTS ix_order_items_order_id
    ON raw.order_items (order_id);

CREATE INDEX IF NOT EXISTS ix_order_items_promotion_id
    ON raw.order_items (promotion_id);

