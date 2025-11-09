import pandas as pd
import logging
from pathlib import Path

# --- PATHS ---
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "products_data.csv"
PREPARED_DATA_DIR = REPO_ROOT / "data" / "prepared"
PREPARED_DATA_PATH = PREPARED_DATA_DIR / "products_prepared.csv"

# --- LOGGING ---
logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_products_data():
    print(f"📂 Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    # Load data
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning Steps ---
    # 1. Remove duplicates
    df.drop_duplicates(inplace=True)

    # 2. Handle missing supplier or category names
    if "Supplier_cat" in df.columns:
        df["Supplier_cat"] = df["Supplier_cat"].fillna("Unknown")

    if "RestockTime_days_num" in df.columns:
        df["RestockTime_days_num"] = pd.to_numeric(df["RestockTime_days_num"], errors="coerce")
        df = df[df["RestockTime_days_num"].notna() & (df["RestockTime_days_num"] > 0)]

    # 3. Handle invalid prices
    if "UnitPrice" in df.columns:
        df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
        df = df[df["UnitPrice"].notna() & (df["UnitPrice"] > 0) & (df["UnitPrice"] < 10000)]

    # --- Save cleaned data ---
    PREPARED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PREPARED_DATA_PATH, index=False)
    print(f"💾 Prepared file saved to: {PREPARED_DATA_PATH}")
    print(f"✅ Final shape: {df.shape}")

    return df


if __name__ == "__main__":
    clean_products_data()
