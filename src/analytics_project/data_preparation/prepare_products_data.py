import pandas as pd
import logging
from pathlib import Path

# --- FIXED PATHS (go up THREE levels now) ---
REPO_ROOT = Path(__file__).resolve().parents[3]  # <- notice 3 here instead of 2
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "products_data.csv"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "products_data_cleaned.csv"

# --- Logging ---
logging.basicConfig(
    filename=REPO_ROOT / "project.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def clean_products_data():
    print(f"Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    df.drop_duplicates(inplace=True)
    if "UnitPrice" in df.columns:
        df = df[(df["UnitPrice"] > 0) & (df["UnitPrice"] < 5000)]

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"✅ Cleaned file saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    clean_products_data()
