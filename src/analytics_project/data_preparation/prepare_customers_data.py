import pandas as pd
import logging
from pathlib import Path

# --- PATHS ---
REPO_ROOT = Path(__file__).resolve().parents[3]  # go up to the repo root
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "customers_data.csv"
PREPARED_DATA_DIR = REPO_ROOT / "data" / "prepared"
PREPARED_DATA_PATH = PREPARED_DATA_DIR / "customers_prepared.csv"

# --- LOGGING ---
logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_customers_data():
    print(f"📂 Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    # Load data
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning Steps ---
    # 1. Remove duplicates
    df.drop_duplicates(inplace=True)

    # 2. Handle missing or invalid regions
    if "Region" in df.columns:
        df["Region"] = df["Region"].fillna("Unknown")

    # 3. Fix invalid invoice numbers
    if "OpenInvoices_num" in df.columns:
        df["OpenInvoices_num"] = pd.to_numeric(df["OpenInvoices_num"], errors="coerce")
        df = df[df["OpenInvoices_num"].notna() & (df["OpenInvoices_num"] >= 0)]

    # 4. Fill missing retention category
    if "RetentionCategory_Cat" in df.columns:
        df["RetentionCategory_Cat"] = df["RetentionCategory_Cat"].fillna("Unspecified")

    # --- Save cleaned data ---
    PREPARED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PREPARED_DATA_PATH, index=False)
    print(f"💾 Prepared file saved to: {PREPARED_DATA_PATH}")
    print(f"✅ Final shape: {df.shape}")

    return df


if __name__ == "__main__":
    clean_customers_data()
