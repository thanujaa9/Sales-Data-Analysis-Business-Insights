"""
PostgreSQL Database Management & ETL Module (Phase 2)
-----------------------------------------------------
Manages database connectivity, schema lifecycle, normalized relational ETL loading,
and CRUD operations for sales data analytics.
"""

import os
import logging
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("DatabaseManager")


def get_db_config() -> Dict[str, Any]:
    """Retrieves database connection configuration from environment."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "dbname": os.getenv("DB_NAME", "sales_analytics_db"),
        "user": os.getenv("DB_USER", os.getenv("USER", "postgres")),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def get_db_connection():
    """Returns a raw psycopg2 database connection."""
    config = get_db_config()
    try:
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


def get_db_engine() -> Engine:
    """Returns a SQLAlchemy engine instance."""
    config = get_db_config()
    user = config["user"]
    password = config["password"]
    host = config["host"]
    port = config["port"]
    dbname = config["dbname"]
    auth = f"{user}:{password}@" if password else f"{user}@"
    url = f"postgresql+psycopg2://{auth}{host}:{port}/{dbname}"
    return create_engine(url)


def init_database(schema_path: str = "database/schema.sql") -> None:
    """Executes schema DDL to create relational tables and indexes."""
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    logger.info(f"Initializing database schema from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
        logger.info("Database schema initialized successfully (customers, products, orders, order_items).")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing schema: {e}")
        raise
    finally:
        conn.close()


def load_cleaned_data_to_postgres(csv_path: str = "data/cleaned_sales.csv") -> Dict[str, int]:
    """
    Extracts, normalizes, and loads cleaned flat sales data into relational PostgreSQL tables:
    1. customers
    2. products
    3. orders
    4. order_items
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {csv_path}")

    logger.info(f"Loading cleaned data from {csv_path} into relational PostgreSQL tables...")
    df = pd.read_csv(csv_path)

    conn = get_db_connection()
    stats = {}

    try:
        with conn.cursor() as cur:
            # 1. Customers
            customers_df = df[[
                "customer_id", "customer_name", "customer_email", "customer_city", "customer_state"
            ]].drop_duplicates(subset=["customer_id"])

            customer_records = [
                (
                    row["customer_id"],
                    row["customer_name"],
                    row["customer_email"],
                    row["customer_city"],
                    row["customer_state"]
                )
                for _, row in customers_df.iterrows()
            ]

            insert_customers_sql = """
                INSERT INTO customers (customer_id, customer_name, customer_email, city, state)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO UPDATE SET
                    customer_name = EXCLUDED.customer_name,
                    customer_email = EXCLUDED.customer_email,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state;
            """
            execute_batch(cur, insert_customers_sql, customer_records)
            stats["customers_loaded"] = len(customer_records)
            logger.info(f"Loaded {len(customer_records):,} unique customers.")

            # 2. Products
            products_df = df[[
                "product_id", "product_name", "category", "unit_price"
            ]].drop_duplicates(subset=["product_id"])

            product_records = [
                (
                    row["product_id"],
                    row["product_name"],
                    row["category"],
                    float(row["unit_price"])
                )
                for _, row in products_df.iterrows()
            ]

            insert_products_sql = """
                INSERT INTO products (product_id, product_name, category, price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category = EXCLUDED.category,
                    price = EXCLUDED.price;
            """
            execute_batch(cur, insert_products_sql, product_records)
            stats["products_loaded"] = len(product_records)
            logger.info(f"Loaded {len(product_records):,} unique products.")

            # 3. Orders
            orders_df = df[[
                "order_id", "customer_id", "order_date", "order_status"
            ]].drop_duplicates(subset=["order_id"])

            order_records = [
                (
                    row["order_id"],
                    row["customer_id"],
                    row["order_date"],
                    row["order_status"]
                )
                for _, row in orders_df.iterrows()
            ]

            insert_orders_sql = """
                INSERT INTO orders (order_id, customer_id, order_date, order_status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING;
            """
            execute_batch(cur, insert_orders_sql, order_records)
            stats["orders_loaded"] = len(order_records)
            logger.info(f"Loaded {len(order_records):,} unique orders.")

            # 4. Order Items
            item_records = [
                (
                    row["order_id"],
                    row["product_id"],
                    int(row["quantity"]),
                    float(row["unit_price"]),
                    float(row["total_amount"])
                )
                for _, row in df.iterrows()
            ]

            insert_items_sql = """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s);
            """
            execute_batch(cur, insert_items_sql, item_records)
            stats["order_items_loaded"] = len(item_records)
            logger.info(f"Loaded {len(item_records):,} order line items.")

        conn.commit()
        logger.info("ETL load into PostgreSQL completed successfully.")
        return stats

    except Exception as e:
        conn.rollback()
        logger.error(f"Error during ETL load: {e}")
        raise
    finally:
        conn.close()


def demonstrate_crud_operations() -> Dict[str, Any]:
    """
    Demonstrates standard CRUD operations (Create, Read, Update, Delete)
    with transaction integrity and constraints checking.
    """
    logger.info("Executing CRUD demonstration...")
    conn = get_db_connection()
    crud_log = {}

    try:
        with conn.cursor() as cur:
            # 1. CREATE: Add test product
            test_prod_id = "PROD-TEST-999"
            cur.execute("""
                INSERT INTO products (product_id, product_name, category, price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET price = EXCLUDED.price
                RETURNING product_id, product_name, price;
            """, (test_prod_id, "Wireless Noise-Cancelling Headphones Pro", "Audio", 249.99))
            created = cur.fetchone()
            crud_log["create"] = f"Created product: {created}"

            # 2. READ: Query newly created product
            cur.execute("SELECT product_id, product_name, category, price FROM products WHERE product_id = %s;", (test_prod_id,))
            read_item = cur.fetchone()
            crud_log["read"] = f"Fetched product: {read_item}"

            # 3. UPDATE: Adjust price with promotional discount
            cur.execute("""
                UPDATE products 
                SET price = %s 
                WHERE product_id = %s 
                RETURNING product_id, price;
            """, (219.99, test_prod_id))
            updated = cur.fetchone()
            crud_log["update"] = f"Updated price to: {updated[1]}"

            # 4. DELETE: Remove test product
            cur.execute("DELETE FROM products WHERE product_id = %s RETURNING product_id;", (test_prod_id,))
            deleted = cur.fetchone()
            crud_log["delete"] = f"Deleted product: {deleted[0]}"

        conn.commit()
        logger.info("CRUD operations verified successfully.")
        return crud_log

    except Exception as e:
        conn.rollback()
        logger.error(f"CRUD demonstration error: {e}")
        raise
    finally:
        conn.close()


def query_dataframe(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Executes a SQL query and returns results as a Pandas DataFrame."""
    engine = get_db_engine()
    return pd.read_sql_query(query, engine, params=params)


if __name__ == "__main__":
    init_database()
    load_cleaned_data_to_postgres()
    crud_result = demonstrate_crud_operations()
    for action, detail in crud_result.items():
        print(f"[{action.upper()}] {detail}")
