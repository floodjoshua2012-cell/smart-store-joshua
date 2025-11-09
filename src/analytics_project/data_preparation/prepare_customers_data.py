import pandas as pd
import logging
from pathlib import Path
from analytics_project.data_scrubber import DataScrubber  # ← use your reusable class

# --- PATHS ---
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
    print(f"📂 Reading: {RAW_DATA_PATH}")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_DATA_PATH}")

    # Load raw data
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Loaded successfully: {df.shape}")

    # Initialize DataScrubber
    scrubber = DataScrubber(df)

    # --- Apply cleaning steps ---
    df = scrubber.remove_duplicate_records()  # remove duplicates
    df = scrubber.handle_missing_data(drop=True)  # drop missing rows
    df = scrubber.filter_column_outliers("OpenInvoices_num", 0, 50)  # remove extreme invoice counts
    df = scrubber.format_column_strings_to_upper_and_trim("Region")  # clean region text
    df = scrubber.format_column_strings_to_upper_and_trim(
        "RetentionCategory_Cat"
    )  # clean category text

    # Save cleaned dataset
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"💾 Cleaned file saved to: {PROCESSED_DATA_PATH}")
    print(f"📉 Final shape: {df.shape}")


if __name__ == "__main__":
    clean_customers_data()
