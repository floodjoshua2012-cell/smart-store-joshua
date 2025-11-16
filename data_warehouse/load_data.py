import sqlite3
import pandas as pd
from pathlib import Path

# Paths
base_path = Path(__file__).resolve().parent
db_path = base_path / "datawarehouse.db"
data_path = base_path.parent / "data" / "prepared"

# Connect to SQLite
conn = sqlite3.connect(db_path)

# Load CSVs
customers = pd.read_csv(data_path / "customers_prepared.csv")
products = pd.read_csv(data_path / "products_prepared.csv")
sales = pd.read_csv(data_path / "sales_prepared.csv")

# Load into tables
customers.to_sql("DimCustomer", conn, if_exists="replace", index=False)
products.to_sql("DimProduct", conn, if_exists="replace", index=False)
sales.to_sql("FactSales", conn, if_exists="replace", index=False)

conn.close()
print("✅ Data loaded successfully into SQLite warehouse.")
