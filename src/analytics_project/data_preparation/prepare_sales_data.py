import pandas as pd
import pandas as pd
import logging
from pathlib import Path

# --- FIXED PATHS ---
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "sales_data.csv"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "sales_data_cleaned.csv"

# --- Logging ---
logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_sales_data():
    print(f"Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning steps ---
    df.drop_duplicates(inplace=True)

    # Convert SaleDate to datetime
    if "SaleDate" in df.columns:
        df["SaleDate"] = pd.to_datetime(df["SaleDate"], errors="coerce")

    # Force SaleAmount to numeric before filtering
    if "SaleAmount" in df.columns:
        df["SaleAmount"] = pd.to_numeric(df["SaleAmount"], errors="coerce")
        df = df[(df["SaleAmount"] >= 0) & (df["SaleAmount"] < 100000)]

    # Fix discount percent — ensure it’s numeric and between 0–1
    if "DiscountPct_num" in df.columns:
        df["DiscountPct_num"] = pd.to_numeric(df["DiscountPct_num"], errors="coerce")
        df.loc[(df["DiscountPct_num"] < 0) | (df["DiscountPct_num"] > 1), "DiscountPct_num"] = None
        df["DiscountPct_num"] = df["DiscountPct_num"].fillna(0.0)

    # Fill missing payment type
    if "PaymentType_cat" in df.columns:
        df["PaymentType_cat"] = df["PaymentType_cat"].fillna("Unknown")

    # --- Save cleaned version ---
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"✅ Cleaned file saved to: {PROCESSED_DATA_PATH}")
    logging.info(f"Cleaned sales data saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    clean_sales_data()
