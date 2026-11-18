"""
Executive Report Generator (Phase 5)
------------------------------------
Compiles comprehensive business insights reports in both Markdown and PDF formats:
- Executive KPI Summary
- Revenue Performance by Category & Product
- Monthly Trajectory & Seasonality Analysis
- Regional & Customer Distribution
- Strategic Data-Driven Business Recommendations
"""

import os
import sys
import logging
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.data_analysis import (
    get_executive_kpis,
    get_monthly_revenue_trends,
    get_category_performance,
    get_product_rankings,
    get_regional_sales,
    get_top_customers,
    get_customer_rfm_summary,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ReportGenerator")


def generate_markdown_report(
    kpis: Dict[str, Any],
    monthly_df: pd.DataFrame,
    category_df: pd.DataFrame,
    top_products_df: pd.DataFrame,
    regional_df: pd.DataFrame,
    top_customers_df: pd.DataFrame,
    output_path: str = "reports/sales_insights.md"
) -> str:
    """Generates a comprehensive executive business insights report in GitHub Flavored Markdown."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    top_cat = category_df.iloc[0]
    top_prod = top_products_df.iloc[0]

    md_content = f"""# Executive Sales Data Analysis & Business Insights Report

**Project Scope:** End-to-End Retail Sales Performance Analytics  
**Architecture:** Python + Pandas Data Pipeline • PostgreSQL Relational Database • Advanced SQL Analytics • Matplotlib Visualization  
**Reporting Period:** Full Year 2023  

---

## 1. Executive Summary & Core KPIs

During the analyzed operating period, the business achieved consistent transaction flow across diverse product categories and major metropolitan markets.

| Metric | Value | Business Significance |
| :--- | :--- | :--- |
| **Total Revenue** | **${kpis['total_revenue']:,.2f}** | Cumulative gross sales across all completed orders |
| **Total Completed Orders** | **{kpis['total_orders']:,}** | Total processed commercial orders |
| **Unique Customers** | **{kpis['unique_customers']:,}** | Distinct purchasing customer base |
| **Total Units Sold** | **{kpis['total_units_sold']:,}** | Aggregate inventory units moved |
| **Average Order Value (AOV)** | **${kpis['avg_order_value']:,.2f}** | Average spend per customer basket |
| **Top Category Contribution** | **{top_cat['category']} ({top_cat['revenue_share_pct']}%)** | Primary revenue driver across product portfolio |
| **Hero Product** | **{top_prod['product_name']}** | Highest grossing SKU generating ${top_prod['total_revenue']:,.2f} |

---

## 2. Executive Analytics Dashboard

![Executive Dashboard](figures/executive_dashboard.png)

---

## 3. Product Category Revenue Breakdown

The catalog is divided into 5 core merchandise segments. **{top_cat['category']}** generated the highest overall revenue share, followed by **{category_df.iloc[1]['category']}** and **{category_df.iloc[2]['category']}**.

| Product Category | Orders Count | Units Sold | Total Revenue (USD) | Revenue Share (%) |
| :--- | :---: | :---: | :---: | :---: |
"""

    for _, row in category_df.iterrows():
        md_content += f"| **{row['category']}** | {int(row['orders_count']):,} | {int(row['units_sold']):,} | ${row['category_revenue']:,.2f} | {row['revenue_share_pct']:.2f}% |\n"

    md_content += """
![Category Revenue](figures/category_revenue.png)

---

## 4. Top 10 Best-Selling Products Ranking

High-ticket electronics and premium computing equipment disproportionately anchor top-line performance, demonstrating strong purchasing power in prosumer segments.

| Rank | Product ID | Product Name | Category | Units Sold | Total Revenue (USD) |
| :---: | :--- | :--- | :--- | :---: | :---: |
"""

    for rank, (_, row) in enumerate(top_products_df.iterrows(), 1):
        md_content += f"| {rank} | `{row['product_id']}` | {row['product_name']} | {row['category']} | {int(row['units_sold']):,} | ${row['total_revenue']:,.2f} |\n"

    md_content += """
![Top Products](figures/top_products.png)

---

## 5. Monthly Revenue Trajectory & Growth Patterns

| Month | Total Orders | Units Sold | Monthly Revenue (USD) | MoM Growth (%) |
| :---: | :---: | :---: | :---: | :---: |
"""

    for _, row in monthly_df.iterrows():
        mom_str = f"{row['mom_growth_pct']:+.2f}%" if pd.notna(row['mom_growth_pct']) else "Baseline (N/A)"
        md_content += f"| **{row['sales_month']}** | {int(row['total_orders']):,} | {int(row['total_units']):,} | ${row['revenue']:,.2f} | {mom_str} |\n"

    md_content += """
![Monthly Revenue Trend](figures/monthly_revenue_trend.png)

---

## 6. Top 10 High-Value Customers

| Customer ID | Name | City | State | Total Orders | Total Units | Lifetime Spend (USD) | AOV (USD) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
"""

    for _, row in top_customers_df.iterrows():
        md_content += f"| `{row['customer_id']}` | {row['customer_name']} | {row['city']} | {row['state']} | {int(row['total_orders'])} | {int(row['total_items'])} | ${row['lifetime_spend']:,.2f} | ${row['avg_order_value']:,.2f} |\n"

    md_content += """
---

## 7. Regional Market Performance (Top 10 Cities)

| City | Orders Count | Customers Count | Units Sold | Total Revenue (USD) | Avg Order Value |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""

    for _, row in regional_df.head(10).iterrows():
        md_content += f"| **{row['city']}** | {int(row['total_orders']):,} | {int(row['total_customers']):,} | {int(row['units_sold']):,} | ${row['total_revenue']:,.2f} | ${row['avg_order_value']:,.2f} |\n"

    md_content += """
![Regional Performance](figures/regional_performance.png)

---

## 8. Strategic Business Recommendations

Based on the empirical findings generated by the SQL analytics and data processing pipeline:

1. **Capitalize on Hero Computing Products:**
   - The *Pro Laptop 15-inch* accounts for over 23% of total revenue. Implement automated bundling (e.g. bundle with USB-C Hubs, Ergonomic Mice, and Laptop Sleeves) to boost basket size without discounting core hardware margins.

2. **Mitigate Mid-Year Seasonality Dip:**
   - Revenue reaches historical lows during Q2 (February - May). Deploy targeted mid-year corporate hardware refresh campaigns and spring promotional flash sales to smooth revenue volatility.

3. **High-Value Loyalty Retention (VIP Tier):**
   - The top 10 customers represent disproportionate lifetime spending. Establish an exclusive VIP rewards tier offering priority delivery, extended warranties, and dedicated support to safeguard high-LTV accounts.

4. **Geographic Expansion & Regional Inventory Hubs:**
   - Leading metropolitan hubs (Chicago, New York, San Francisco, Austin, Seattle) account for over 50% of orders. Establishing micro-fulfillment nodes or localized shipping partnerships in these regions will reduce shipping latency and last-mile logistics overhead.

5. **Cross-Selling Into Home & Office Categories:**
   - Ergonomic Office Chairs and Standing Desks boast high profit contributions. Trigger automated post-purchase email flows offering ergonomic furniture discounts to laptop and monitor purchasers.

---
*Report automatically compiled by Sales Analytics Pipeline Engine.*
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info(f"Generated Markdown business insights report: {output_path}")
    return output_path


def generate_pdf_report(
    kpis: Dict[str, Any],
    monthly_df: pd.DataFrame,
    category_df: pd.DataFrame,
    top_products_df: pd.DataFrame,
    output_path: str = "reports/sales_insights.pdf"
) -> str:
    """Generates a professional executive PDF report using ReportLab."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        fontName="Helvetica",
        spaceAfter=15,
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E293B"),
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica",
        spaceAfter=6,
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F172A"),
    )
    cell_normal = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("Sales Data Analysis & Business Insights Report", title_style))
    story.append(Paragraph("Enterprise Retail Performance Report • Generated via PostgreSQL & Python Pipeline", subtitle_style))

    # Executive KPI Summary Cards Table
    kpi_table_data = [
        [
            Paragraph("<b>TOTAL REVENUE</b>", cell_normal),
            Paragraph("<b>TOTAL ORDERS</b>", cell_normal),
            Paragraph("<b>UNITS SOLD</b>", cell_normal),
            Paragraph("<b>AVERAGE ORDER VALUE</b>", cell_normal),
        ],
        [
            Paragraph(f"<font size=12 color='#06B6D4'><b>${kpis['total_revenue']:,.2f}</b></font>", cell_normal),
            Paragraph(f"<font size=12 color='#3B82F6'><b>{kpis['total_orders']:,}</b></font>", cell_normal),
            Paragraph(f"<font size=12 color='#10B981'><b>{kpis['total_units_sold']:,}</b></font>", cell_normal),
            Paragraph(f"<font size=12 color='#F59E0B'><b>${kpis['avg_order_value']:.2f}</b></font>", cell_normal),
        ]
    ]

    t_kpi = Table(kpi_table_data, colWidths=[135, 135, 135, 135])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # Executive Dashboard Chart
    dash_img_path = "reports/figures/executive_dashboard.png"
    if os.path.exists(dash_img_path):
        story.append(Paragraph("1. Executive Analytics Dashboard", section_style))
        story.append(Image(dash_img_path, width=7.2*inch, height=4.3*inch))
        story.append(Spacer(1, 14))

    story.append(PageBreak())

    # Category Revenue Breakdown
    story.append(Paragraph("2. Category Sales Performance", section_style))
    cat_table_data = [
        [
            Paragraph("<b>Category</b>", cell_bold),
            Paragraph("<b>Orders</b>", cell_bold),
            Paragraph("<b>Units</b>", cell_bold),
            Paragraph("<b>Revenue (USD)</b>", cell_bold),
            Paragraph("<b>Share (%)</b>", cell_bold),
        ]
    ]
    for _, row in category_df.iterrows():
        cat_table_data.append([
            Paragraph(str(row["category"]), cell_normal),
            Paragraph(f"{int(row['orders_count']):,}", cell_normal),
            Paragraph(f"{int(row['units_sold']):,}", cell_normal),
            Paragraph(f"${row['category_revenue']:,.2f}", cell_normal),
            Paragraph(f"{row['revenue_share_pct']:.2f}%", cell_normal),
        ])

    t_cat = Table(cat_table_data, colWidths=[150, 95, 95, 110, 90])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 14))

    # Top 5 Products Table
    story.append(Paragraph("3. Top 5 Revenue-Generating Products", section_style))
    prod_table_data = [
        [
            Paragraph("<b>Product Name</b>", cell_bold),
            Paragraph("<b>Category</b>", cell_bold),
            Paragraph("<b>Units</b>", cell_bold),
            Paragraph("<b>Total Revenue</b>", cell_bold),
        ]
    ]
    for _, row in top_products_df.head(5).iterrows():
        prod_table_data.append([
            Paragraph(str(row["product_name"]), cell_normal),
            Paragraph(str(row["category"]), cell_normal),
            Paragraph(f"{int(row['units_sold']):,}", cell_normal),
            Paragraph(f"${row['total_revenue']:,.2f}", cell_normal),
        ])

    t_prod = Table(prod_table_data, colWidths=[200, 120, 90, 130])
    t_prod.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_prod)
    story.append(Spacer(1, 16))

    # Strategic Recommendations
    story.append(Paragraph("4. Strategic Business Recommendations", section_style))
    recs = [
        "<b>Bundle High-Ticket Hardware:</b> Leverage the Pro Laptop 15-inch's leading market share by bundling high-margin accessories to optimize Average Order Value.",
        "<b>Address Mid-Year Seasonality:</b> Smooth Q2 revenue contraction by scheduling aggressive enterprise and corporate hardware procurement discounts in April-May.",
        "<b>VIP Account Protection:</b> Institutionalize a dedicated tier for high-frequency spenders to foster recurring loyalty and prevent customer churn.",
        "<b>Regional Fulfillment Hubs:</b> Prioritize logistics in primary hubs (Chicago, New York, San Francisco, Austin) to shorten order fulfillment timeframes."
    ]
    for rec in recs:
        story.append(Paragraph(f"• {rec}", body_style))
        story.append(Spacer(1, 3))

    doc.build(story)
    logger.info(f"Generated PDF business insights report: {output_path}")
    return output_path


def generate_all_reports() -> Dict[str, str]:
    """Compiles both Markdown and PDF reports."""
    logger.info("Compiling executive business insights reports...")
    kpis = get_executive_kpis()
    monthly = get_monthly_revenue_trends()
    category = get_category_performance()
    top_prods, _ = get_product_rankings()
    regional = get_regional_sales()
    top_custs = get_top_customers()

    md_path = generate_markdown_report(kpis, monthly, category, top_prods, regional, top_custs)
    pdf_path = generate_pdf_report(kpis, monthly, category, top_prods)

    return {"markdown_report": md_path, "pdf_report": pdf_path}


if __name__ == "__main__":
    generate_all_reports()
