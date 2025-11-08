import pandas as pd
import logging
from pathlib import Path

# --- FIXED PATHS (same structure as products) ---
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "customers_data.csv"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "customers_data_cleaned.csv"

# --- Logging ---
logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_customers_data():
    print(f"Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning steps ---
    df.drop_duplicates(inplace=True)

    # Convert JoinDate to datetime
    if "JoinDate" in df.columns:
        df["JoinDate"] = pd.to_datetime(df["JoinDate"], errors="coerce")

    # Handle missing or invalid invoice counts
    if "OpenInvoices_num" in df.columns:
        df["OpenInvoices_num"] = (
            pd.to_numeric(df["OpenInvoices_num"], errors="coerce").fillna(0).astype(int)
        )

    # Replace missing retention category with "Unknown"
    if "RetentionCategory_Cat" in df.columns:
        df["RetentionCategory_Cat"] = df["RetentionCategory_Cat"].fillna("Unknown")

    # --- Save cleaned version ---
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"✅ Cleaned file saved to: {PROCESSED_DATA_PATH}")
    logging.info(f"Cleaned customers data saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    clean_customers_data()
