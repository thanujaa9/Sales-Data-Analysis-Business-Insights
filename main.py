"""
Sales Data Analysis & Business Insights - Master Pipeline
---------------------------------------------------------
Executes the complete end-to-end data engineering and analytics pipeline:
1. Phase 1: Cleans raw e-commerce sales dataset and exports structured CSV.
2. Phase 2: Creates PostgreSQL relational schema and loads normalized tables.
3. Phase 3: Executes comprehensive SQL analytics queries.
4. Phase 4: Extracts business metrics into Pandas and creates Matplotlib charts.
5. Phase 5: Compiles executive business insights reports (Markdown & PDF).
"""

import os
import sys
import time
import logging

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_cleaning import clean_sales_data
from src.database import init_database, load_cleaned_data_to_postgres, demonstrate_crud_operations
from src.data_analysis import run_full_analysis
from src.visualizations import generate_all_visualizations
from src.report_generator import generate_all_reports

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("PipelineOrchestrator")


def run_pipeline():
    start_time = time.time()
    print("=" * 75)
    print("🚀 STARTING SALES DATA ANALYSIS & BUSINESS INSIGHTS PIPELINE")
    print("=" * 75)

    # Step 1: Data Cleaning & Validation (Phase 1)
    print("\n[PHASE 1] Cleaning and validating raw sales dataset...")
    raw_csv = "data/raw_sales.csv"
    clean_csv = "data/cleaned_sales.csv"
    if not os.path.exists(raw_csv):
        print("Raw sales dataset missing! Generating initial raw dataset...")
        from data.generate_raw_data import generate_raw_sales_data
        generate_raw_sales_data(raw_csv)

    clean_df, audit = clean_sales_data(raw_csv, clean_csv)
    print(f"  ✓ Processed {audit['initial_rows']:,} raw records.")
    print(f"  ✓ Dropped {audit['duplicates_removed']:,} duplicates.")
    print(f"  ✓ Dropped {audit['missing_or_null_dropped']:,} records with missing keys.")
    print(f"  ✓ Dropped {audit['invalid_numeric_dropped']:,} records with invalid price/quantity.")
    print(f"  ✓ Final valid records: {audit['final_rows']:,} | Revenue: {audit['total_revenue']:,.2f}")

    # Step 2: PostgreSQL Database & Relational ETL (Phase 2)
    print("\n[PHASE 2] Initializing PostgreSQL schema & executing relational ETL...")
    init_database("database/schema.sql")
    stats = load_cleaned_data_to_postgres(clean_csv)
    print(f"  ✓ Customers loaded:    {stats['customers_loaded']:,}")
    print(f"  ✓ Products loaded:     {stats['products_loaded']:,}")
    print(f"  ✓ Orders loaded:       {stats['orders_loaded']:,}")
    print(f"  ✓ Order items loaded:  {stats['order_items_loaded']:,}")

    print("\n[PHASE 2.1] Verifying CRUD operations and constraints...")
    crud = demonstrate_crud_operations()
    print(f"  ✓ CRUD Create/Read/Update/Delete verified: {list(crud.keys())}")

    # Step 3 & 4: SQL Business Analytics & Metrics (Phase 3 & 4)
    print("\n[PHASE 3 & 4] Running SQL analytics & Python business metrics...")
    analysis_results = run_full_analysis()

    # Step 4: Matplotlib Visualizations (Phase 4)
    print("\n[PHASE 4.1] Generating presentation-grade visual charts...")
    saved_charts = generate_all_visualizations("reports/figures")
    for name, path in saved_charts.items():
        print(f"  ✓ Created chart: {path}")

    # Step 5: Executive Business Insights Report (Phase 5)
    print("\n[PHASE 5] Compiling executive insights reports (Markdown & PDF)...")
    reports = generate_all_reports()
    print(f"  ✓ Markdown report generated: {reports['markdown_report']}")
    print(f"  ✓ PDF report generated:      {reports['pdf_report']}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("=" * 75)


if __name__ == "__main__":
    run_pipeline()
