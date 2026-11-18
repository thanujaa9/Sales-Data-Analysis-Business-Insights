-- ====================================================================
-- Phase 3: SQL Business Analytics & Insights
-- Comprehensive analytical queries demonstrating aggregations, multi-table JOINs,
-- date manipulation, Common Table Expressions (CTEs), and Window Functions.
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Total Revenue, Total Orders, Total Units Sold, and Overall AOV
-- Concepts: SUM(), COUNT(), AVG(), ROUND()
-- --------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.total_price), 2) AS total_revenue,
    ROUND(SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2) AS average_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id;


-- --------------------------------------------------------------------
-- 2. Top 5 Best-Selling Products by Revenue
-- Concepts: JOIN, GROUP BY, ORDER BY, LIMIT
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.total_price), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;


-- --------------------------------------------------------------------
-- 3. Monthly Revenue Trends and Transaction Volume
-- Concepts: DATE_TRUNC(), TO_CHAR(), GROUP BY, Date Functions
-- --------------------------------------------------------------------
SELECT 
    TO_CHAR(DATE_TRUNC('month', o.order_date), 'YYYY-MM') AS sales_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.total_price), 2) AS monthly_revenue,
    ROUND(AVG(oi.total_price), 2) AS avg_item_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY sales_month ASC;


-- --------------------------------------------------------------------
-- 4. Revenue & Sales Share by Product Category
-- Concepts: JOIN, GROUP BY, SUM(), Percentage of Total calculation
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 5. Top 10 High-Value Customers by Lifetime Spending
-- Concepts: Multi-table JOIN, Aggregation, ORDER BY
-- --------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_items_purchased,
    ROUND(SUM(oi.total_price), 2) AS lifetime_spend,
    ROUND(AVG(oi.total_price), 2) AS avg_transaction_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name, c.city, c.state
ORDER BY lifetime_spend DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- 6. Repeat Customers Analysis
-- Concepts: GROUP BY, COUNT(), HAVING, Subquery Aggregations
-- --------------------------------------------------------------------
-- 6a. Customers with more than 1 order (Repeat Buyers)
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(oi.total_price), 2) AS total_spend
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(o.order_id) > 1
ORDER BY total_orders DESC, total_spend DESC;

-- 6b. Overall Repeat Purchase Rate
WITH customer_orders_summary AS (
    SELECT 
        customer_id,
        COUNT(order_id) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT 
    COUNT(CASE WHEN order_count > 1 THEN 1 END) AS repeat_customers_count,
    COUNT(*) AS total_customers_count,
    ROUND(100.0 * COUNT(CASE WHEN order_count > 1 THEN 1 END) / COUNT(*), 2) AS repeat_customer_rate_pct
FROM customer_orders_summary;


-- --------------------------------------------------------------------
-- 7. Month-Over-Month (MoM) Revenue Growth Rate
-- Concepts: CTEs, LAG() Window Function, COALESCE(), Percentage Difference
-- --------------------------------------------------------------------
WITH monthly_revenue_cte AS (
    SELECT 
        TO_CHAR(DATE_TRUNC('month', o.order_date), 'YYYY-MM') AS sales_month,
        ROUND(SUM(oi.total_price), 2) AS current_month_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT 
    sales_month,
    current_month_revenue,
    LAG(current_month_revenue, 1) OVER (ORDER BY sales_month) AS previous_month_revenue,
    ROUND(
        current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY sales_month), 
        2
    ) AS absolute_change,
    ROUND(
        100.0 * (current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY sales_month)) 
        / NULLIF(LAG(current_month_revenue, 1) OVER (ORDER BY sales_month), 0),
        2
    ) AS mom_growth_pct
FROM monthly_revenue_cte
ORDER BY sales_month ASC;


-- --------------------------------------------------------------------
-- 8. Product Sales Ranking Within Each Category
-- Concepts: Window Functions, DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)
-- --------------------------------------------------------------------
WITH category_product_sales AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.total_price), 2) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS category_rank,
    product_name,
    total_units_sold,
    total_revenue
FROM category_product_sales
ORDER BY category, category_rank ASC;


-- --------------------------------------------------------------------
-- 9. Regional / City-Level Sales Performance
-- Concepts: Multi-table JOIN, GROUP BY city/state, Aggregation
-- --------------------------------------------------------------------
SELECT 
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.total_price), 2) AS total_revenue,
    ROUND(SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.city, c.state
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- 10. Customer RFM (Recency, Frequency, Monetary) Segmentation
-- Concepts: CTEs, Window Functions (NTILE), Date Arithmetic, CASE Statements
-- --------------------------------------------------------------------
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
        -- Higher score = better (lower recency days is better)
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency_orders ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_total ASC) AS m_score
    FROM customer_rfm_base
)
SELECT 
    customer_id,
    customer_name,
    recency_days,
    frequency_orders,
    monetary_total,
    r_score,
    f_score,
    m_score,
    CASE 
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Top Champions'
        WHEN f_score >= 3 AND m_score >= 2 THEN 'Loyal High Spenders'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'Recent Buyers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churn Warning'
        ELSE 'General Customers'
    END AS rfm_segment
FROM rfm_scores
ORDER BY monetary_total DESC
LIMIT 15;
