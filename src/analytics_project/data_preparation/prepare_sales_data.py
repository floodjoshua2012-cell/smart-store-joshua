import pandas as pd
import logging
from pathlib import Path

# --- PATHS ---
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "sales_data.csv"
PREPARED_DATA_DIR = REPO_ROOT / "data" / "prepared"
PREPARED_DATA_PATH = PREPARED_DATA_DIR / "sales_prepared.csv"

# --- LOGGING ---
logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_sales_data():
    print(f"📂 Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    # Load data
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning Steps ---
    df.drop_duplicates(inplace=True)

    # 1. Convert and filter SaleAmount
    if "SaleAmount" in df.columns:
        df["SaleAmount"] = pd.to_numeric(df["SaleAmount"], errors="coerce")
        df = df[df["SaleAmount"].notna() & (df["SaleAmount"] > 0) & (df["SaleAmount"] < 100000)]

    # 2. Handle missing PaymentType_cat
    if "PaymentType_cat" in df.columns:
        df["PaymentType_cat"] = df["PaymentType_cat"].fillna("Unknown")

    # 3. Convert SaleDate to datetime if needed
    if "SaleDate" in df.columns:
        df["SaleDate"] = pd.to_datetime(df["SaleDate"], errors="coerce")

    # --- Save cleaned data ---
    PREPARED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PREPARED_DATA_PATH, index=False)
    print(f"💾 Prepared file saved to: {PREPARED_DATA_PATH}")
    print(f"✅ Final shape: {df.shape}")

    return df


if __name__ == "__main__":
    clean_sales_data()
