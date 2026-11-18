"""
Python Business Analytics Engine (Phase 4)
------------------------------------------
Connects Python to PostgreSQL, extracts business metrics via optimized SQL queries,
loads into Pandas DataFrames, and performs statistical and comparative analysis.
"""

import os
import sys
import logging
from typing import Dict, Any, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from src.database import query_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("DataAnalysis")


def get_executive_kpis() -> Dict[str, Any]:
    """Retrieves macro-level executive business KPIs."""
    query = """
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS unique_customers,
            SUM(oi.quantity) AS total_units_sold,
            ROUND(SUM(oi.total_price), 2) AS total_revenue,
            ROUND(SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id;
    """
    df = query_dataframe(query)
    row = df.iloc[0]
    return {
        "total_revenue": float(row["total_revenue"]),
        "total_orders": int(row["total_orders"]),
        "unique_customers": int(row["unique_customers"]),
        "total_units_sold": int(row["total_units_sold"]),
        "avg_order_value": float(row["avg_order_value"]),
    }


def get_monthly_revenue_trends() -> pd.DataFrame:
    """Computes monthly revenue, volume, and Month-over-Month (MoM) growth rates."""
    query = """
        WITH monthly_cte AS (
            SELECT 
                TO_CHAR(DATE_TRUNC('month', o.order_date), 'YYYY-MM') AS sales_month,
                COUNT(DISTINCT o.order_id) AS total_orders,
                SUM(oi.quantity) AS total_units,
                ROUND(SUM(oi.total_price), 2) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY DATE_TRUNC('month', o.order_date)
        )
        SELECT 
            sales_month,
            total_orders,
            total_units,
            revenue,
            LAG(revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
            ROUND(
                100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY sales_month)) 
                / NULLIF(LAG(revenue, 1) OVER (ORDER BY sales_month), 0),
                2
            ) AS mom_growth_pct
        FROM monthly_cte
        ORDER BY sales_month ASC;
    """
    return query_dataframe(query)


def get_category_performance() -> pd.DataFrame:
    """Computes revenue, units sold, and overall revenue contribution by product category."""
    query = """
        SELECT 
            p.category,
            COUNT(DISTINCT o.order_id) AS orders_count,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.total_price), 2) AS category_revenue,
            ROUND(
                100.0 * SUM(oi.total_price) / SUM(SUM(oi.total_price)) OVER (), 
                2
            ) AS revenue_share_pct
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        GROUP BY p.category
        ORDER BY category_revenue DESC;
    """
    return query_dataframe(query)


def get_product_rankings(top_n: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Retrieves top-performing and lowest-performing products by revenue."""
    top_query = f"""
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            p.price AS unit_price,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.total_price), 2) AS total_revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name, p.category, p.price
        ORDER BY total_revenue DESC
        LIMIT {top_n};
    """
    bottom_query = f"""
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            p.price AS unit_price,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.total_price), 2) AS total_revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name, p.category, p.price
        ORDER BY total_revenue ASC
        LIMIT 5;
    """
    top_df = query_dataframe(top_query)
    bottom_df = query_dataframe(bottom_query)
    return top_df, bottom_df


def get_top_customers(limit: int = 10) -> pd.DataFrame:
    """Retrieves top customers by cumulative spending and order frequency."""
    query = f"""
        SELECT 
            c.customer_id,
            c.customer_name,
            c.city,
            c.state,
            COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(oi.quantity) AS total_items,
            ROUND(SUM(oi.total_price), 2) AS lifetime_spend,
            ROUND(SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id, c.customer_name, c.city, c.state
        ORDER BY lifetime_spend DESC
        LIMIT {limit};
    """
    return query_dataframe(query)


def get_regional_sales(top_n: int = 10) -> pd.DataFrame:
    """Aggregates sales performance by city/region."""
    query = f"""
        SELECT 
            c.city,
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT c.customer_id) AS total_customers,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.total_price), 2) AS total_revenue,
            ROUND(SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.city
        ORDER BY total_revenue DESC
        LIMIT {top_n};
    """
    return query_dataframe(query)


def get_customer_rfm_summary() -> pd.DataFrame:
    """Returns customer segmentation based on Recency, Frequency, Monetary (RFM) scores."""
    query = """
        WITH customer_rfm_base AS (
            SELECT 
                c.customer_id,
                c.customer_name,
                ((SELECT MAX(order_date) FROM orders) - MAX(o.order_date)) AS recency_days,
                COUNT(DISTINCT o.order_id) AS frequency_orders,
                ROUND(SUM(oi.total_price), 2) AS monetary_total
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_id, c.customer_name
        ),
        rfm_scores AS (
            SELECT 
                customer_id,
                customer_name,
                recency_days,
                frequency_orders,
                monetary_total,
                NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
                NTILE(4) OVER (ORDER BY frequency_orders ASC) AS f_score,
                NTILE(4) OVER (ORDER BY monetary_total ASC) AS m_score
            FROM customer_rfm_base
        )
        SELECT 
            CASE 
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
                WHEN f_score >= 3 AND m_score >= 2 THEN 'Loyal High Spenders'
                WHEN r_score >= 3 AND f_score <= 2 THEN 'Recent Buyers'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churn Warning'
                ELSE 'General Customers'
            END AS segment,
            COUNT(*) AS customer_count,
            ROUND(SUM(monetary_total), 2) AS segment_revenue,
            ROUND(AVG(monetary_total), 2) AS avg_customer_spend
        FROM rfm_scores
        GROUP BY 
            CASE 
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
                WHEN f_score >= 3 AND m_score >= 2 THEN 'Loyal High Spenders'
                WHEN r_score >= 3 AND f_score <= 2 THEN 'Recent Buyers'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churn Warning'
                ELSE 'General Customers'
            END
        ORDER BY segment_revenue DESC;
    """
    return query_dataframe(query)


def run_full_analysis() -> Dict[str, Any]:
    """Executes the full suite of business analytics and logs summary tables."""
    logger.info("Executing comprehensive business analytics suite...")

    kpis = get_executive_kpis()
    monthly = get_monthly_revenue_trends()
    category = get_category_performance()
    top_prods, bottom_prods = get_product_rankings()
    top_custs = get_top_customers()
    regional = get_regional_sales()
    rfm = get_customer_rfm_summary()

    print("\n" + "="*70)
    print(" EXECUTIVE SALES KPIS")
    print("="*70)
    print(f"Total Revenue:       ${kpis['total_revenue']:,.2f}")
    print(f"Total Orders:        {kpis['total_orders']:,}")
    print(f"Unique Customers:    {kpis['unique_customers']:,}")
    print(f"Total Units Sold:    {kpis['total_units_sold']:,}")
    print(f"Average Order Value: ${kpis['avg_order_value']:,.2f}")

    print("\n" + "="*70)
    print(" REVENUE BY PRODUCT CATEGORY")
    print("="*70)
    print(category.to_string(index=False))

    print("\n" + "="*70)
    print(" TOP 5 BEST-SELLING PRODUCTS")
    print("="*70)
    print(top_prods[["product_id", "product_name", "category", "units_sold", "total_revenue"]].head(5).to_string(index=False))

    print("\n" + "="*70)
    print(" CUSTOMER RFM SEGMENTATION")
    print("="*70)
    print(rfm.to_string(index=False))

    return {
        "kpis": kpis,
        "monthly": monthly,
        "category": category,
        "top_products": top_prods,
        "bottom_products": bottom_prods,
        "top_customers": top_custs,
        "regional": regional,
        "rfm": rfm,
    }


if __name__ == "__main__":
    run_full_analysis()
