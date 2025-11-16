import logging
import pandas as pd

logger = logging.getLogger(__name__)


def insert_customers(df, cursor):
    """
    Insert cleaned customer rows into DW customer table.
    """

    # remove duplicate customer IDs
    df = df.drop_duplicates(subset=["CustomerID"])

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

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO customer (
                customer_id, name, region, join_date,
                open_invoices_num, retention_category
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["customer_id"]),
                row["name"],
                row["region"],
                str(row["join_date"]),
                str(row["open_invoices_num"]),  # ← FIXED
                row["retention_category"],
            ),
        )

    logger.info("Customers inserted successfully.")
