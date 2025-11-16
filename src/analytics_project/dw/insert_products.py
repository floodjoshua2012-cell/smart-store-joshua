import sqlite3
import pandas as pd
from analytics_project.utils_logger import logger


def insert_products(df, cursor):
    """
    Insert cleaned product rows into DW product table.
    """

    # Remove duplicates
    df = df.drop_duplicates(subset=["ProductID"])

    # Rename columns to match DW schema
    df = df.rename(
        columns={
            "ProductID": "product_id",
            "ProductName": "name",
            "Category": "category",
            "UnitPrice": "unit_price_usd",
            "RestockTime_days_num": "restock_days",
            "Supplier_cat": "supplier",
        }
    )

    # Convert numeric fields
    df["unit_price_usd"] = (
        pd.to_numeric(df["unit_price_usd"], errors="coerce").fillna(0).astype(float)
    )

    df["restock_days"] = pd.to_numeric(df["restock_days"], errors="coerce").fillna(0).astype(int)

    # Insert row by row
    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO product (
                product_id, name, category, unit_price_usd,
                supplier, restock_days
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["product_id"]),
                row["name"],
                row["category"],
                float(row["unit_price_usd"]),
                row.get("supplier", None),
                int(row.get("restock_days", 0)),
            ),
        )

    logger.info("Products inserted successfully.")
