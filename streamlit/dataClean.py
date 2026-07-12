import os
import glob
import pandas as pd

_here = os.path.dirname(os.path.abspath(__file__))

# Load and combine all three CSV files
_csv_files = sorted(glob.glob(os.path.join(_here, "daily_sales_data_*.csv")))
df = pd.concat([pd.read_csv(f) for f in _csv_files], ignore_index=True)

# Keep only Pink Morsels
df = df[df["product"].str.strip().str.lower() == "pink morsel"].copy()

# Compute sales = price * quantity (strip leading $ from price first)
df["price"] = df["price"].str.replace("$", "", regex=False).astype(float)
df["sales"] = df["price"] * df["quantity"]

# Keep only the required columns
df = df[["sales", "date", "region"]]

# Write output
output_path = os.path.join(_here, "clean_data.csv")
df.to_csv(output_path, index=False)
print(f"Wrote {len(df)} rows to {output_path}")
