import pandas as pd
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "customers_data.csv"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "customers_data_cleaned.csv"

logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_customers_data():
    print(f"Reading: {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning steps ---
    df.drop_duplicates(inplace=True)

    # Drop missing or invalid CustomerIDs
    if "CustomerID" in df.columns:
        df = df[df["CustomerID"].notna()]

    # Convert JoinDate and drop future ones
    if "JoinDate" in df.columns:
        df["JoinDate"] = pd.to_datetime(df["JoinDate"], errors="coerce")
        df = df[df["JoinDate"] <= pd.Timestamp.today()]

    # Convert invoice count and drop unrealistic ones
    invoice_col = [c for c in df.columns if "invoice" in c.lower()]
    if invoice_col:
        col = invoice_col[0]
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Drop customers with > 20 open invoices (simulating bad data)
        df = df[df[col] <= 20]

    # Force-remove 2% of rows to simulate cleaning loss
    drop_n = max(1, int(len(df) * 0.02))
    df = df.iloc[:-drop_n]

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"✅ Cleaned file saved to: {PROCESSED_DATA_PATH}")
    print(f"📉 Rows removed: {drop_n}")
    logging.info(f"Cleaned customers data saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    clean_customers_data()
