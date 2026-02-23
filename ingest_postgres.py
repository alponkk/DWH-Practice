import os

import pandas as pd
from sqlalchemy import Engine, create_engine
from sqlalchemy.dialects.postgresql import BOOLEAN, INTEGER, NUMERIC, TEXT, TIMESTAMP


def build_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine for the local Postgres instance
    using the hard‑coded connection details for this DWH practice project.
    """
    host = "localhost"
    port = "5432"
    db = "data_warehouse"
    user = "dwh_admin"
    password = "dwh_admin"

    return create_engine(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}")


def _to_bool_series(s: pd.Series) -> pd.Series:
    """
    Normalize a pandas Series into a nullable boolean dtype, handling common
    string and numeric representations such as 'True'/'False', '1'/'0', and 1/0.
    """
    if pd.api.types.is_bool_dtype(s):
        return s
    if pd.api.types.is_numeric_dtype(s):
        return s.astype("boolean")
    if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
        mapped = s.map(
            {
                True: True,
                False: False,
                "True": True,
                "False": False,
                "true": True,
                "false": False,
                "t": True,
                "f": False,
                "1": True,
                "0": False,
                1: True,
                0: False,
                None: None,
                "": None,
            }
        )
        return mapped.astype("boolean")
    return s.astype("boolean")


def load_csv_to_table(
    *,
    engine: Engine,
    table_name: str,
    csv_path: str,
    dtype: dict,
    parse_dates: list[str] | None = None,
    boolean_cols: list[str] | None = None,
    schema: str = "raw",
) -> None:
    """
    Stream a CSV file into a Postgres table in chunks, optionally parsing
    date columns and converting specified columns to booleans.
    """
    print(f"Loading {os.path.basename(csv_path)} -> {schema}.{table_name}")

    chunksize = int("5000")

    for chunk in pd.read_csv(
        csv_path,
        chunksize=chunksize,
        parse_dates=parse_dates or None,
        na_values=["", " ", "NA", "N/A", "null", "NULL"],
        keep_default_na=True,
    ):
        for col in (boolean_cols or []):
            if col in chunk.columns:
                chunk[col] = _to_bool_series(chunk[col])

        chunk.to_sql(
            table_name,
            con=engine,
            schema=schema,
            if_exists="append",
            index=False,
            dtype=dtype,
            method="multi",
        )


def main() -> None:
    """
    Entry point: locate the CSV files in the data directory, define table
    metadata, and load each CSV into its corresponding Postgres table.
    """
    data_dir = r"d:\DE Projects\DWH Practice\Data Sources"
    if not os.path.isdir(data_dir):
        raise SystemExit(f"Could not find data directory: {data_dir}")

    schema = "data_warehouse"
    engine = build_engine()

    tables: list[dict] = [
        {
            "table_name": "customers",
            "csv_path": os.path.join(data_dir, "customers.csv"),
            "parse_dates": ["registration_date", "last_purchase_date"],
            "boolean_cols": ["email_opt_in", "sms_opt_in", "push_opt_in"],
            "dtype": {
                "customer_id": INTEGER(),
                "first_name": TEXT(),
                "last_name": TEXT(),
                "email": TEXT(),
                "phone_number": TEXT(),
                "registration_date": TIMESTAMP(),
                "customer_segment": TEXT(),
                "preferred_channel": TEXT(),
                "age_group": TEXT(),
                "income_level": TEXT(),
                "avg_order_value": NUMERIC(),
                "promo_sensitivity": NUMERIC(),
                "email_opt_in": BOOLEAN(),
                "sms_opt_in": BOOLEAN(),
                "push_opt_in": BOOLEAN(),
                "last_purchase_date": TIMESTAMP(),
                "total_lifetime_orders": INTEGER(),
                "preferred_category": TEXT(),
            },
        },
        {
            "table_name": "promotions",
            "csv_path": os.path.join(data_dir, "promotions.csv"),
            "parse_dates": ["start_date", "end_date"],
            "boolean_cols": [],
            "dtype": {
                "promotion_id": INTEGER(),
                "campaign_name": TEXT(),
                "promo_type": TEXT(),
                "discount_value": NUMERIC(),
                "min_order_value": NUMERIC(),
                "start_date": TIMESTAMP(),
                "end_date": TIMESTAMP(),
                "campaign_duration_days": INTEGER(),
                "target_segment": TEXT(),
                "campaign_channel": TEXT(),
                "campaign_objective": TEXT(),
                "target_category": TEXT(),
                "expected_response_rate": NUMERIC(),
                "budget_allocated": NUMERIC(),
                "cost_per_acquisition": NUMERIC(),
            },
        },
        {
            "table_name": "orders",
            "csv_path": os.path.join(data_dir, "orders.csv"),
            "parse_dates": ["order_date"],
            "boolean_cols": ["attributed_to_promo"],
            "dtype": {
                "order_id": INTEGER(),
                "customer_id": INTEGER(),
                "order_date": TIMESTAMP(),
                "order_status": TEXT(),
                "promotion_id": INTEGER(),
                "order_channel": TEXT(),
                "order_value": NUMERIC(),
                "attributed_to_promo": BOOLEAN(),
                "customer_segment_at_time": TEXT(),
            },
        },
        {
            "table_name": "order_items",
            "csv_path": os.path.join(data_dir, "order_items.csv"),
            "parse_dates": [],
            "boolean_cols": ["attributed_to_promo"],
            "dtype": {
                "order_item_id": INTEGER(),
                "order_id": INTEGER(),
                "product_id": INTEGER(),
                "product_category": TEXT(),
                "quantity": INTEGER(),
                "unit_price": NUMERIC(),
                "promotion_id": INTEGER(),
                "attributed_to_promo": BOOLEAN(),
            },
        },
    ]

    for t in tables:
        csv_path = t["csv_path"]
        if not os.path.isfile(csv_path):
            raise SystemExit(f"Missing file: {csv_path}")
        load_csv_to_table(engine=engine, schema=schema, **t)

    print("Done.")


if __name__ == "__main__":
    main()
