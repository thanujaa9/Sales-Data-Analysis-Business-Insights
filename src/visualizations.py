"""
Sales Data Visualizations Module (Phase 4)
------------------------------------------
Generates modern, presentation-grade visual charts using Matplotlib:
- Monthly Revenue Trend & MoM Growth
- Product Category Revenue Distribution
- Top 10 Best-Selling Products Ranking
- Regional & City-Level Sales Performance
- Consolidated Executive Analytics Dashboard (4-panel)
"""

import os
import sys
import logging
from typing import Dict, Any

# Ensure project root is in sys.path for direct script execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from src.data_analysis import (
    get_monthly_revenue_trends,
    get_category_performance,
    get_product_rankings,
    get_regional_sales,
    get_executive_kpis,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("Visualizations")

# Modern Dark Analytics Theme Palette (Inspired by modern fintech & SaaS dashboards)
BG_DARK = "#0F172A"       # Slate 900
PANEL_DARK = "#1E293B"    # Slate 800
TEXT_LIGHT = "#F8FAFC"    # Slate 50
TEXT_MUTED = "#94A3B8"    # Slate 400
GRID_COLOR = "#334155"    # Slate 700

COLOR_CYAN = "#06B6D4"     # Cyan 500
COLOR_BLUE = "#3B82F6"     # Blue 500
COLOR_VIOLET = "#8B5CF6"   # Violet 500
COLOR_EMERALD = "#10B981"  # Emerald 500
COLOR_AMBER = "#F59E0B"    # Amber 500
COLOR_ROSE = "#F43F5E"     # Rose 500

PALETTE = [COLOR_CYAN, COLOR_VIOLET, COLOR_BLUE, COLOR_EMERALD, COLOR_AMBER, COLOR_ROSE]


def setup_dark_style(fig, ax_list):
    """Applies a consistent modern dark theme to figure and axis objects."""
    fig.patch.set_facecolor(BG_DARK)
    for ax in ax_list:
        ax.set_facecolor(PANEL_DARK)
        ax.tick_params(colors=TEXT_MUTED, labelsize=10)
        ax.xaxis.label.set_color(TEXT_LIGHT)
        ax.yaxis.label.set_color(TEXT_LIGHT)
        ax.title.set_color(TEXT_LIGHT)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)
            spine.set_linewidth(1.0)
        ax.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.5, zorder=0)


def plot_monthly_revenue_trend(df: pd.DataFrame, output_dir: str = "reports/figures") -> str:
    """Plots monthly revenue trend line with gradient area fill and MoM indicators."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "monthly_revenue_trend.png")

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    setup_dark_style(fig, [ax1])

    x = df["sales_month"]
    y = df["revenue"]

    # Plot revenue line
    ax1.plot(x, y, color=COLOR_CYAN, linewidth=2.8, marker="o", markersize=6, 
             label="Monthly Revenue", zorder=4)
    ax1.fill_between(x, y, color=COLOR_CYAN, alpha=0.15, zorder=3)

    # Highlight max and min months
    max_idx = y.idxmax()
    min_idx = y.idxmin()

    ax1.annotate(
        f"Peak: {y[max_idx]:,.0f}",
        xy=(x[max_idx], y[max_idx]),
        xytext=(0, 15), textcoords="offset points",
        ha="center", fontsize=10, fontweight="bold",
        color="#38BDF8",
        arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=1.5)
    )

    ax1.annotate(
        f"Low: {y[min_idx]:,.0f}",
        xy=(x[min_idx], y[min_idx]),
        xytext=(0, -25), textcoords="offset points",
        ha="center", fontsize=10, fontweight="bold",
        color=COLOR_ROSE,
        arrowprops=dict(arrowstyle="->", color=COLOR_ROSE, lw=1.5)
    )

    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"{val*1e-3:.0f}K"))
    ax1.set_title("Monthly Revenue Trajectory (2023)", fontsize=16, fontweight="bold", pad=20)
    ax1.set_xlabel("Month", fontsize=12, labelpad=10)
    ax1.set_ylabel("Revenue", fontsize=12, labelpad=10)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BG_DARK, edgecolor="none")
    plt.close()
    logger.info(f"Saved monthly revenue trend plot: {out_path}")
    return out_path


def plot_category_distribution(df: pd.DataFrame, output_dir: str = "reports/figures") -> str:
    """Plots product category revenue share with a stylized donut chart."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "category_revenue.png")

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)

    wedges, texts, autotexts = ax.pie(
        df["category_revenue"],
        labels=df["category"],
        autopct="%1.1f%%",
        startangle=140,
        colors=PALETTE[:len(df)],
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor=BG_DARK, linewidth=2)
    )

    for text in texts:
        text.set_color(TEXT_LIGHT)
        text.set_fontsize(11)
        text.set_fontweight("medium")

    for autotext in autotexts:
        autotext.set_color(BG_DARK)
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")

    total_revenue = df["category_revenue"].sum()
    ax.text(0, 0, f"Total\n{total_revenue*1e-3:.0f}K", ha="center", va="center",
            fontsize=13, fontweight="bold", color=TEXT_LIGHT)

    ax.set_title("Revenue Share by Product Category", fontsize=16, fontweight="bold", color=TEXT_LIGHT, pad=20)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BG_DARK, edgecolor="none")
    plt.close()
    logger.info(f"Saved category revenue plot: {out_path}")
    return out_path


def plot_top_products(df: pd.DataFrame, output_dir: str = "reports/figures") -> str:
    """Plots top 10 selling products horizontal bar chart."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "top_products.png")

    df_sorted = df.sort_values(by="total_revenue", ascending=True).tail(10)

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    setup_dark_style(fig, [ax])

    bars = ax.barh(df_sorted["product_name"], df_sorted["total_revenue"], color=COLOR_BLUE, height=0.65, zorder=3)

    # Highlight top 1 product with distinct gradient
    bars[-1].set_color(COLOR_CYAN)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 3000, bar.get_y() + bar.get_height() / 2,
                f"{width:,.0f}",
                va="center", ha="left", fontsize=9.5, fontweight="semibold", color=TEXT_LIGHT)

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"{val*1e-3:.0f}K"))
    ax.set_xlim(0, df_sorted["total_revenue"].max() * 1.15)
    ax.set_title("Top 10 Products by Total Revenue", fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Total Revenue", fontsize=12, labelpad=10)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BG_DARK, edgecolor="none")
    plt.close()
    logger.info(f"Saved top products plot: {out_path}")
    return out_path


def plot_regional_performance(df: pd.DataFrame, output_dir: str = "reports/figures") -> str:
    """Plots top 10 cities by sales revenue with order counts."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "regional_performance.png")

    df_sorted = df.head(10).sort_values(by="total_revenue", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    setup_dark_style(fig, [ax])

    bars = ax.barh(df_sorted["city"], df_sorted["total_revenue"], color=COLOR_VIOLET, height=0.65, zorder=3)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 2000, bar.get_y() + bar.get_height() / 2,
                f"{width:,.0f}",
                va="center", ha="left", fontsize=9.5, fontweight="semibold", color=TEXT_LIGHT)

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"{val*1e-3:.0f}K"))
    ax.set_xlim(0, df_sorted["total_revenue"].max() * 1.15)
    ax.set_title("Top 10 Cities by Revenue Performance", fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Revenue", fontsize=12, labelpad=10)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BG_DARK, edgecolor="none")
    plt.close()
    logger.info(f"Saved regional performance plot: {out_path}")
    return out_path


def generate_executive_dashboard(
    kpis: Dict[str, Any],
    monthly_df: pd.DataFrame,
    category_df: pd.DataFrame,
    top_products_df: pd.DataFrame,
    regional_df: pd.DataFrame,
    output_dir: str = "reports/figures"
) -> str:
    """
    Generates a consolidated 4-panel executive sales analytics dashboard
    incorporating KPI stat cards, revenue trends, category share, and top products.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "executive_dashboard.png")

    fig = plt.figure(figsize=(18, 11), dpi=300)
    fig.patch.set_facecolor(BG_DARK)

    # Grid layout: Top banner for KPIs, bottom 2x2 for analytics
    gs = fig.add_gridspec(3, 2, height_ratios=[0.35, 1, 1], hspace=0.35, wspace=0.25)

    # 1. Header & KPI Cards Banner
    ax_banner = fig.add_subplot(gs[0, :])
    ax_banner.set_facecolor(PANEL_DARK)
    ax_banner.axis("off")
    for spine in ax_banner.spines.values():
        spine.set_visible(False)

    # Title
    ax_banner.text(0.02, 0.72, "SALES ANALYTICS & BUSINESS INSIGHTS DASHBOARD", 
                   fontsize=18, fontweight="bold", color=TEXT_LIGHT)
    ax_banner.text(0.02, 0.40, "Executive Performance Overview • PostgreSQL + Python Engine", 
                   fontsize=11, color=TEXT_MUTED)

    # KPI Metric Cards
    kpi_cards = [
        ("TOTAL REVENUE", f"{kpis['total_revenue']:,.2f}", COLOR_CYAN),
        ("TOTAL ORDERS", f"{kpis['total_orders']:,}", COLOR_BLUE),
        ("UNITS SOLD", f"{kpis['total_units_sold']:,}", COLOR_EMERALD),
        ("AVG ORDER VALUE", f"{kpis['avg_order_value']:.2f}", COLOR_AMBER),
    ]

    card_x_positions = [0.50, 0.63, 0.76, 0.89]
    for i, (label, val, col) in enumerate(kpi_cards):
        cx = card_x_positions[i]
        ax_banner.text(cx, 0.70, label, fontsize=9.5, fontweight="bold", color=TEXT_MUTED, ha="center")
        ax_banner.text(cx, 0.28, val, fontsize=14, fontweight="bold", color=col, ha="center")

    # 2. Monthly Revenue Trend (Top Left)
    ax_trend = fig.add_subplot(gs[1, 0])
    setup_dark_style(fig, [ax_trend])
    x = monthly_df["sales_month"]
    y = monthly_df["revenue"]
    ax_trend.plot(x, y, color=COLOR_CYAN, marker="o", linewidth=2.4, zorder=4)
    ax_trend.fill_between(x, y, color=COLOR_CYAN, alpha=0.18, zorder=3)
    ax_trend.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, p: f"{v*1e-3:.0f}K"))
    ax_trend.set_title("Monthly Revenue Trajectory", fontsize=13, fontweight="bold", pad=12)
    ax_trend.tick_params(axis="x", rotation=45, labelsize=8.5)

    # 3. Category Revenue Share Donut (Top Right)
    ax_cat = fig.add_subplot(gs[1, 1])
    ax_cat.set_facecolor(PANEL_DARK)
    wedges, texts, autotexts = ax_cat.pie(
        category_df["category_revenue"],
        labels=category_df["category"],
        autopct="%1.1f%%",
        startangle=140,
        colors=PALETTE[:len(category_df)],
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor=PANEL_DARK, linewidth=2)
    )
    for text in texts:
        text.set_color(TEXT_LIGHT)
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_color(PANEL_DARK)
        autotext.set_fontsize(8.5)
        autotext.set_fontweight("bold")
    ax_cat.set_title("Category Revenue Distribution", fontsize=13, fontweight="bold", color=TEXT_LIGHT, pad=12)

    # 4. Top 5 Products (Bottom Left)
    ax_prod = fig.add_subplot(gs[2, 0])
    setup_dark_style(fig, [ax_prod])
    p_top = top_products_df.sort_values(by="total_revenue", ascending=True).tail(5)
    bars_p = ax_prod.barh(p_top["product_name"], p_top["total_revenue"], color=COLOR_BLUE, height=0.6, zorder=3)
    bars_p[-1].set_color(COLOR_CYAN)
    ax_prod.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, p: f"{v*1e-3:.0f}K"))
    ax_prod.set_title("Top 5 Revenue Generators", fontsize=13, fontweight="bold", pad=12)

    # 5. Top 5 Regional Cities (Bottom Right)
    ax_reg = fig.add_subplot(gs[2, 1])
    setup_dark_style(fig, [ax_reg])
    r_top = regional_df.head(5).sort_values(by="total_revenue", ascending=True)
    ax_reg.barh(r_top["city"], r_top["total_revenue"], color=COLOR_VIOLET, height=0.6, zorder=3)
    ax_reg.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, p: f"{v*1e-3:.0f}K"))
    ax_reg.set_title("Top 5 Cities by Revenue", fontsize=13, fontweight="bold", pad=12)

    plt.savefig(out_path, facecolor=BG_DARK, edgecolor="none", bbox_inches="tight")
    plt.close()
    logger.info(f"Saved executive dashboard composite image: {out_path}")
    return out_path


def generate_all_visualizations(output_dir: str = "reports/figures") -> Dict[str, str]:
    """Generates and saves the complete set of visual analytical charts."""
    logger.info("Generating analytical charts suite...")
    kpis = get_executive_kpis()
    monthly = get_monthly_revenue_trends()
    category = get_category_performance()
    top_prods, _ = get_product_rankings()
    regional = get_regional_sales()

    saved_paths = {
        "monthly_trend": plot_monthly_revenue_trend(monthly, output_dir),
        "category_distribution": plot_category_distribution(category, output_dir),
        "top_products": plot_top_products(top_prods, output_dir),
        "regional_performance": plot_regional_performance(regional, output_dir),
        "executive_dashboard": generate_executive_dashboard(
            kpis, monthly, category, top_prods, regional, output_dir
        ),
    }

    logger.info(f"All visualizations successfully created in: {output_dir}")
    return saved_paths


if __name__ == "__main__":
    generate_all_visualizations()
