# DWH Practice — Data Warehouse Project

A small **data warehouse (DWH) practice project** for E‑commerce sales, customers, and marketing promotions. It uses **PostgreSQL** as the database, **Python** for ingestion, and **SQL** for schema setup and analytical queries.

---

## Project Overview

| Component | Purpose |
|-----------|--------|
| **Data Sources** | CSV files (customers, orders, order items, promotions) used as the source of truth. |
| **init_postgres.sql** | Creates the database schema and tables (raw layer) and indexes. |
| **ingest_postgres.py** | Loads CSV data into PostgreSQL (data_warehouse schema) in chunks. |
| **datamart.sql** | Example analytical queries (top customers by order value, top products by revenue). |
| **requirements.txt** | Python dependencies for the ingestion script. |

**Domain**: E‑commerce sales, customer segments, and promotion campaigns. The structure supports a star-schema style warehouse with **customers** and **promotions** as dimensions and **orders** and **order_items** as fact tables.

---

## Prerequisites

- **PostgreSQL** (local instance, e.g. on `localhost:5432`)
- **Python 3.x** (with pip)
- Database `data_warehouse` and user `dwh_admin` / password `dwh_admin` (or adjust connection details in `ingest_postgres.py`)

Create the database and user if needed:

```sql
CREATE USER dwh_admin WITH PASSWORD 'dwh_admin';
CREATE DATABASE data_warehouse OWNER dwh_admin;
```

---

## Setup and Run Order

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database (optional raw layer)**  
   Run `init_postgres.sql` against your Postgres instance (e.g. with `psql` or your SQL client). This creates the `raw` schema, tables, foreign keys, and indexes.

3. **Ingest CSV data**  
   Place the CSV files in the `Data Sources` folder (see below), then run:
   ```bash
   python ingest_postgres.py
   ```
   This loads data into the **data_warehouse** schema. Tables are created on first run via `to_sql(..., if_exists="append")`.

4. **Run analytical queries**  
   Execute the queries in `datamart.sql` against the `data_warehouse` schema (e.g. in `psql` or a SQL client).

---

## Repository Layout

```
DWH Practice/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── init_postgres.sql         # Schema and table definitions (raw layer)
├── ingest_postgres.py        # CSV → Postgres ingestion script
├── datamart.sql              # Example analytics queries
├── Data Sources Documentation.md   # Detailed docs for each CSV
└── Data Sources/             # Source CSV files
    ├── customers.csv
    ├── orders.csv
    ├── order_items.csv
    └── promotions.csv
```

---

## Script and File Reference

### `init_postgres.sql`

**Purpose**: One-time setup of the database structures for the DWH practice dataset.

- Creates the **`raw`** schema.
- Creates four tables with primary keys and foreign keys:
  - **`raw.customers`** — one row per customer (dimension).
  - **`raw.promotions`** — one row per promotion/campaign (dimension).
  - **`raw.orders`** — one row per order; references `customers` and `promotions` (fact).
  - **`raw.order_items`** — one row per order line item; references `orders` and `promotions` (fact).
- Adds indexes on foreign key columns (`customer_id`, `promotion_id`, `order_id`) to speed up joins.

**When to run**: Once, before any loading. Note: the Python ingestion script loads into the **`data_warehouse`** schema, not `raw`; you can use `raw` for a separate staging layer or align schema names if you prefer a single layer.

---

### `ingest_postgres.py`

**Purpose**: Loads the four CSV files from `Data Sources` into PostgreSQL in the **`data_warehouse`** schema.

- **Connection**: Uses SQLAlchemy with `psycopg`; connection parameters are hard-coded (`localhost`, port `5432`, database `data_warehouse`, user `dwh_admin`, password `dwh_admin`). Change these in `build_engine()` if your environment differs.
- **Flow**:
  1. Builds the engine and checks that the `Data Sources` directory exists.
  2. For each configured table (customers, promotions, orders, order_items):
     - Reads the corresponding CSV in **chunks** (5000 rows) to limit memory use.
     - Optionally **parses date columns** and **converts specified columns to boolean** (e.g. `email_opt_in`, `attributed_to_promo`).
     - Writes each chunk with `to_sql(..., if_exists="append", ...)` and explicit dtypes (INTEGER, TEXT, NUMERIC, TIMESTAMP, BOOLEAN).
- **Tables and CSVs**:
  - `data_warehouse.customers` ← `customers.csv` (dates: `registration_date`, `last_purchase_date`; booleans: `email_opt_in`, `sms_opt_in`, `push_opt_in`).
  - `data_warehouse.promotions` ← `promotions.csv` (dates: `start_date`, `end_date`).
  - `data_warehouse.orders` ← `orders.csv` (dates: `order_date`; boolean: `attributed_to_promo`).
  - `data_warehouse.order_items` ← `order_items.csv` (boolean: `attributed_to_promo`).

**When to run**: After the database and (if used) `raw` schema are set up. Ensure all four CSVs exist in `Data Sources`; the script exits with a clear error if any file is missing.

---

### `datamart.sql`

**Purpose**: Example **analytical queries** on the `data_warehouse` schema.

1. **Top 5 customers by order value**  
   Joins `data_warehouse.orders` and `data_warehouse.customers`, concatenates first and last name, sums order value per customer, and returns the top 5 by `order_value` (descending).

2. **Top 10 products by revenue in 2025**  
   Joins `data_warehouse.orders` and `data_warehouse.order_items`, filters by `EXTRACT(YEAR FROM order_date) = 2025`, groups by `product_id` and `product_category`, computes revenue as `SUM(quantity * unit_price)`, and returns the top 10 by that revenue.

You can run these as-is or adapt them for reporting and dashboards.

---

### `Data Sources/`

**Purpose**: Holds the **source CSV files** consumed by `ingest_postgres.py`.

| File | Description |
|------|-------------|
| **customers.csv** | One row per customer: ID, name, contact, segment, channel preferences, opt-ins, lifetime orders, preferred category, etc. |
| **orders.csv** | One row per order: ID, customer, date, status, promotion, channel, value, attribution flag, segment snapshot. |
| **order_items.csv** | One row per line item: order, product, category, quantity, unit price, promotion, attribution flag. |
| **promotions.csv** | One row per promotion: campaign name, type, discount, dates, target segment/channel/category, budget, response rate, etc. |

For full column definitions, keys, and relationships, see **`Data Sources Documentation.md`** in the project root.

---

### `requirements.txt`

**Purpose**: Python package list for the ingestion script.

| Package | Role |
|---------|------|
| **pandas** | Read CSVs in chunks and write to Postgres via `to_sql`. |
| **SQLAlchemy** | Database abstraction and engine; used with the Postgres dialect. |
| **psycopg[binary]** | PostgreSQL driver used by SQLAlchemy for the connection. |

Install with: `pip install -r requirements.txt`.

---

## Schema Note: `raw` vs `data_warehouse`

- **`init_postgres.sql`** creates tables in the **`raw`** schema (e.g. `raw.customers`, `raw.orders`).
- **`ingest_postgres.py`** loads into the **`data_warehouse`** schema (e.g. `data_warehouse.customers`, `data_warehouse.orders`).
- **`datamart.sql`** reads from **`data_warehouse`**.

So the current flow is: CSVs → `data_warehouse` (via the Python script). The `raw` schema is available if you want a separate staging layer (e.g. copy from CSV into `raw`, then transform into `data_warehouse` in a later step). Table structures in `raw` and the definitions used in the ingestion script are aligned so you can reuse or adapt the same schema in both if needed.

---

## Quick Reference: What Each File Does

| File / Folder | One-line description |
|---------------|------------------------|
| **init_postgres.sql** | Creates `raw` schema, tables (customers, promotions, orders, order_items), FKs, and indexes. |
| **ingest_postgres.py** | Reads CSVs from `Data Sources`, loads them into `data_warehouse` in chunks with type and date/boolean handling. |
| **datamart.sql** | Two example queries: top 5 customers by order value, top 10 products by revenue in 2025. |
| **Data Sources/** | CSV files: customers, orders, order_items, promotions. |
| **requirements.txt** | Dependencies: pandas, SQLAlchemy, psycopg[binary]. |
| **Data Sources Documentation.md** | Detailed documentation of each CSV’s columns, keys, and relationships. |

---

## License and Use

This is a practice project for learning data warehouse setup, ingestion, and analytics. Adjust connection strings, paths, and schema names to match your own environment.
