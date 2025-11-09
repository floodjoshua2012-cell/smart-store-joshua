import pandas as pd
from pathlib import Path
from analytics_project.data_scrubber import DataScrubber

# --- Define paths ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --- Function to process any file ---
def process_file(file_name: str, numeric_limits: dict = None, fill_value="N/A"):
    raw_path = RAW_DIR / file_name
    processed_path = PROCESSED_DIR / file_name.replace(".csv", "_cleaned.csv")

    print(f"\n📂 Reading: {raw_path}")
    df = pd.read_csv(raw_path)

    scrubber = DataScrubber(df)

    # Run cleaning steps separately
    df = scrubber.remove_duplicate_records()
    df = scrubber.handle_missing_data(fill_value=fill_value)

    # Apply outlier filtering if limits provided
    if numeric_limits:
        for col, (low, high) in numeric_limits.items():
            if col in df.columns:
                df = scrubber.filter_column_outliers(col, low, high)

    df.to_csv(processed_path, index=False)
    print(f"✅ Cleaned file saved: {processed_path} ({df.shape[0]} rows)")


# --- Main function ---
def main():
    print("🚀 Starting unified data cleaning process...\n")

    # Customers
    process_file(
        "customers_data.csv",
        numeric_limits={"OpenInvoices": (0, 10000), "RetentionRate": (0, 1)},
        fill_value="N/A",
    )

    # Products
    process_file("products_data.csv", numeric_limits={"RestockQuantity": (0, 1000)}, fill_value=0)

    # Sales
    process_file("sales_data.csv", numeric_limits={"DiscountPercent": (0, 1)}, fill_value=0)

    print("\n🎯 All files cleaned successfully!")


# --- Run main if executed directly ---
if __name__ == "__main__":
    main()
