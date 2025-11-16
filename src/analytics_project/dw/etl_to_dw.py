"""
ETL to Data Warehouse (P4)
Loads cleaned data from data/processed/ into a SQLite data warehouse.
"""

from pathlib import Path
import sqlite3
import pandas as pd
from loguru import logger

# ---------------------------------------------------
# PATH SETUP
# ---------------------------------------------------

# etl_to_dw.py is at: src/analytics_project/dw/etl_to_dw.py
# parents[0] = dw
# parents[1] = analytics_project
# parents[2] = src
# parents[3] = repo root
REPO_ROOT = Path(__file__).resolve().parents[3]

DW_DIR = REPO_ROOT / "data_warehouse"
DW_DIR.mkdir(parents=True, exist_ok=True)

DW_PATH = DW_DIR / "datawarehouse.db"

logger.info(f"DW_PATH resolved to: {DW_PATH}")

# Cleaned files
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
CUSTOMERS_CSV = PROCESSED_DIR / "customers_data_cleaned.csv"
PRODUCTS_CSV = PROCESSED_DIR / "products_data_cleaned.csv"
SALES_CSV = PROCESSED_DIR / "sales_data_cleaned.csv"


# ---------------------------------------------------
# SCHEMA CREATION
# ---------------------------------------------------


def create_tables(cursor: sqlite3.Cursor) -> None:
    """Create dimension and fact tables if they do not exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            region TEXT,
            join_date TEXT,
            open_invoices_num TEXT,
            retention_category TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            unit_price_usd REAL,
            restock_days INTEGER,
            supplier TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sale (
            sale_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            sale_amount_usd REAL,
            sale_date TEXT,
            payment_type TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
            FOREIGN KEY (product_id) REFERENCES product(product_id)
        );
        """
    )


# ---------------------------------------------------
# INSERT FUNCTIONS
# ---------------------------------------------------


def insert_customers(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """
    Insert cleaned customer rows into customer dimension table.
    """

    # Remove duplicate customer IDs
    if "CustomerID" in df.columns:
        df = df.drop_duplicates(subset=["CustomerID"])

    # Rename columns from CSV to DW schema
    df = df.rename(
        columns={
            "CustomerID": "customer_id",
            "Name": "name",
            "Region": "region",
            "JoinDate": "join_date",
            "OpenInvoices_num": "open_invoices_num",
            "RetentionCategory_Cat": "retention_category",
        }
    )

    # Only enforce numeric for customer_id
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df = df[df["customer_id"].notna()]

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO customer (
                customer_id,
                name,
                region,
                join_date,
                open_invoices_num,
                retention_category
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["customer_id"]),
                row.get("name"),
                row.get("region"),
                str(row.get("join_date")),
                # Do not cast invoices to int - keep as text to avoid 'Loyal' crashes
                None
                if pd.isna(row.get("open_invoices_num"))
                else str(row.get("open_invoices_num")),
                row.get("retention_category"),
            ),
        )

    logger.info("Customers inserted successfully.")


def insert_products(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """
    Insert cleaned product rows into product dimension table.
    """

    if "ProductID" in df.columns:
        df = df.drop_duplicates(subset=["ProductID"])

    df = df.rename(
        columns={
            "ProductID": "product_id",
            "ProductName": "product_name",
            "Category": "category",
            "UnitPrice": "unit_price_usd",
            "RestockTime_days_num": "restock_days",
            "Supplier_cat": "supplier",
        }
    )

    # Enforce numeric where appropriate
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["unit_price_usd"] = pd.to_numeric(df["unit_price_usd"], errors="coerce")
    df["restock_days"] = pd.to_numeric(df["restock_days"], errors="coerce")

    df = df[df["product_id"].notna()]

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO product (
                product_id,
                product_name,
                category,
                unit_price_usd,
                restock_days,
                supplier
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["product_id"]),
                row.get("product_name"),
                row.get("category"),
                None if pd.isna(row.get("unit_price_usd")) else float(row.get("unit_price_usd")),
                None if pd.isna(row.get("restock_days")) else int(row.get("restock_days")),
                row.get("supplier"),
            ),
        )

    logger.info("Products inserted successfully.")


def insert_sales(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """
    Insert cleaned sales rows into sale fact table.
    """

    df = df.rename(
        columns={
            "TransactionID": "sale_id",
            "CustomerID": "customer_id",
            "ProductID": "product_id",
            "SaleAmount": "sale_amount_usd",
            "SaleDate": "sale_date",
            "PaymentType_cat": "payment_type",
        }
    )

    if "sale_id" in df.columns:
        df = df.drop_duplicates(subset=["sale_id"])

    # Numeric enforcement for IDs and amounts
    df["sale_id"] = pd.to_numeric(df["sale_id"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["sale_amount_usd"] = pd.to_numeric(df["sale_amount_usd"], errors="coerce")

    df = df[
        df["sale_id"].notna()
        & df["customer_id"].notna()
        & df["product_id"].notna()
        & df["sale_amount_usd"].notna()
    ]

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO sale (
                sale_id,
                customer_id,
                product_id,
                sale_amount_usd,
                sale_date,
                payment_type
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["sale_id"]),
                int(row["customer_id"]),
                int(row["product_id"]),
                float(row["sale_amount_usd"]),
                str(row.get("sale_date")),
                row.get("payment_type"),
            ),
        )

    logger.info("Sales inserted successfully.")


# ---------------------------------------------------
# MAIN ETL FUNCTION
# ---------------------------------------------------


def create_and_load_dw() -> None:
    """Create DW schema and load cleaned data."""
    logger.info("Connecting to DW...")
    conn = sqlite3.connect(DW_PATH)
    cursor = conn.cursor()

    try:
        logger.info("Creating tables...")
        create_tables(cursor)

        logger.info("Loading cleaned CSVs...")

        customers_df = pd.read_csv(CUSTOMERS_CSV)
        products_df = pd.read_csv(PRODUCTS_CSV)
        sales_df = pd.read_csv(SALES_CSV)

        insert_customers(customers_df, cursor)
        insert_products(products_df, cursor)
        insert_sales(sales_df, cursor)

        conn.commit()
        logger.info("DW load complete.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    finally:
        conn.close()
        logger.info("Connection closed.")


if __name__ == "__main__":
    create_and_load_dw()
