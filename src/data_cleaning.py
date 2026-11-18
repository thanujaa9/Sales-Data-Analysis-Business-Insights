"""
Data Cleaning & Transformation Pipeline (Phase 1)
-------------------------------------------------
Cleans and validates raw e-commerce sales records:
- Deduplicates identical records
- Strips dirty currency characters ($, commas) and formats numeric fields
- Detects and drops records with invalid or negative prices/quantities
- Normalizes inconsistent date formats into ISO 8601 (YYYY-MM-DD)
- Handles missing/null values in key dimensions
- Standardizes categorical casing and whitespace
- Computes line-item total sales amounts
- Exports a clean, relational-ready CSV dataset
"""

import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("DataCleaning")


def clean_sales_data(
    input_file: str = "data/raw_sales.csv",
    output_file: str = "data/cleaned_sales.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes end-to-end cleaning and validation on raw sales CSV.
    
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned DataFrame and quality audit metrics.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found at: {input_file}")

    logger.info(f"Loading raw sales dataset from {input_file}...")
    df = pd.read_csv(input_file)
    initial_rows = len(df)
    logger.info(f"Initial raw record count: {initial_rows:,}")

    audit_metrics: Dict[str, Any] = {"initial_rows": initial_rows}

    # 1. Deduplication
    duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    audit_metrics["duplicates_removed"] = int(duplicates_count)
    logger.info(f"Removed {duplicates_count:,} duplicate records.")

    # 2. String trimming & categorical normalization
    string_cols = ["customer_name", "customer_email", "customer_city", 
                   "customer_state", "product_name", "category", "order_status"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Title-case category names to resolve dirty casing variations
    df["category"] = df["category"].str.title()
    df["order_status"] = df["order_status"].str.title()

    # 3. Clean numeric fields (unit_price and quantity)
    # Strip currency signs, commas, whitespace
    df["unit_price"] = (
        df["unit_price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    # 4. Handle Missing Key Identifiers & Nulls
    # Drop rows where customer_id, order_id, product_id, price or quantity are NaN / blank
    missing_mask = (
        df["order_id"].isna() | (df["order_id"] == "") | (df["order_id"] == "nan") |
        df["customer_id"].isna() | (df["customer_id"] == "") | (df["customer_id"] == "nan") |
        df["product_id"].isna() | (df["product_id"] == "") | (df["product_id"] == "nan") |
        df["unit_price"].isna() |
        df["quantity"].isna()
    )
    missing_rows = int(missing_mask.sum())
    audit_metrics["missing_or_null_dropped"] = missing_rows
    df = df[~missing_mask].copy()
    logger.info(f"Dropped {missing_rows:,} records with missing required keys or numeric values.")

    # 5. Filter invalid prices and quantities (must be strictly positive)
    invalid_numeric_mask = (df["unit_price"] <= 0) | (df["quantity"] <= 0)
    invalid_numeric_count = int(invalid_numeric_mask.sum())
    audit_metrics["invalid_numeric_dropped"] = invalid_numeric_count
    df = df[~invalid_numeric_mask].copy()
    logger.info(f"Dropped {invalid_numeric_count:,} records with non-positive price or quantity.")

    # Convert quantity to integer
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].round(2)

    # 6. Parse and standardize dates
    # Uses flexible mixed date parsing to handle mixed formats
    df["order_date"] = pd.to_datetime(
        df["order_date"].astype(str).str.strip(),
        format="mixed",
        errors="coerce"
    )
    unparseable_dates = int(df["order_date"].isna().sum())
    if unparseable_dates > 0:
        logger.warning(f"Dropping {unparseable_dates} rows with unparseable order dates.")
        df = df[df["order_date"].notna()].copy()
    audit_metrics["unparseable_dates_dropped"] = unparseable_dates

    # Format date as standard ISO YYYY-MM-DD
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    # 7. Compute Total Sales Amount
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)

    # 8. Sort cleanly by order_date and order_id
    df = df.sort_values(by=["order_date", "order_id"]).reset_index(drop=True)

    final_rows = len(df)
    total_revenue = float(df["total_amount"].sum())
    audit_metrics["final_rows"] = final_rows
    audit_metrics["total_revenue"] = total_revenue

    logger.info(f"Data cleaning complete! Valid clean records: {final_rows:,}")
    logger.info(f"Total processed revenue: {total_revenue:,.2f}")

    # Ensure output directory exists and save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    logger.info(f"Saved cleaned dataset to: {output_file}")

    return df, audit_metrics


if __name__ == "__main__":
    clean_sales_data()
