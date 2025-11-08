import pandas as pd
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "products_data.csv"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "products_data_cleaned.csv"

logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_products_data():
    print(f"Reading: {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # --- Cleaning steps ---
    df.drop_duplicates(inplace=True)

    # Drop missing or invalid product IDs
    if "ProductID" in df.columns:
        df = df[df["ProductID"].notna()]

    # Detect and clean price column
    price_col = [c for c in df.columns if "price" in c.lower()]
    if price_col:
        col = price_col[0]
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df[(df[col] > 0) & (df[col] < 10000)]

    # Remove products with missing category or supplier
    for c in ["Category", "Supplier_cat"]:
        if c in df.columns:
            df = df[df[c].notna()]

    # Force-remove 5% of rows to simulate cleaning loss
    drop_n = max(1, int(len(df) * 0.05))
    df = df.iloc[:-drop_n]

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"✅ Cleaned file saved to: {PROCESSED_DATA_PATH}")
    print(f"📉 Rows removed: {drop_n}")
    logging.info(f"Cleaned products data saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    clean_products_data()
