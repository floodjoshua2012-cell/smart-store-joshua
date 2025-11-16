import pandas as pd
import sqlite3
from loguru import logger


def insert_sales(df, cursor):
    """
    Insert cleaned sales rows into DW sales fact table.
    """

    # Correct column names based on your actual CSV
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

    # Drop duplicate sale IDs
    df = df.drop_duplicates(subset=["sale_id"])

    # Clean numeric types safely
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["sale_amount_usd"] = pd.to_numeric(df["sale_amount_usd"], errors="coerce")

    # Convert bad/missing IDs to None instead of crashing
    df["customer_id"] = df["customer_id"].fillna(-1)
    df["product_id"] = df["product_id"].fillna(-1)

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO sale (
                sale_id, customer_id, product_id,
                sale_amount_usd, sale_date, payment_type
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["sale_id"]),
                int(row["customer_id"]),
                int(row["product_id"]),
                float(row["sale_amount_usd"]),
                str(row["sale_date"]),
                row["payment_type"],
            ),
        )

    logger.info("Sales inserted successfully.")
