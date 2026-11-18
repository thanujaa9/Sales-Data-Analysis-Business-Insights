"""
Raw Sales Dataset Generator
Generates a realistic, imperfect retail sales dataset with deliberate anomalies
(missing values, duplicates, mixed date formats, dirty currency strings, invalid numbers)
to showcase realistic data cleaning with Pandas.
"""

import random
import csv
from datetime import datetime, timedelta

def generate_raw_sales_data(output_path: str = "data/raw_sales.csv", num_records: int = 2200):
    random.seed(42)

    categories = {
        "Electronics": [
            ("PROD-001", "4K Ultra HD Monitor", 349.99),
            ("PROD-002", "Noise Cancelling Headphones", 199.99),
            ("PROD-003", "Wireless Charging Station", 49.99),
            ("PROD-004", "Smart Security Camera", 129.99),
            ("PROD-005", "Portable Bluetooth Speaker", 79.99),
        ],
        "Computers": [
            ("PROD-006", "Pro Laptop 15-inch", 1299.99),
            ("PROD-007", "Mechanical Gaming Keyboard", 119.99),
            ("PROD-008", "Ergonomic Wireless Mouse", 69.99),
            ("PROD-009", "USB-C Multiport Dock", 89.99),
            ("PROD-010", "External SSD 1TB", 109.99),
        ],
        "Office Supplies": [
            ("PROD-011", "Ergonomic Mesh Office Chair", 249.99),
            ("PROD-012", "Motorized Standing Desk", 499.99),
            ("PROD-013", "Adjustable Monitor Arm", 59.99),
            ("PROD-014", "Desk Organizer Set", 29.99),
            ("PROD-015", "LED Desk Lamp with Dimmer", 39.99),
        ],
        "Home & Kitchen": [
            ("PROD-016", "Smart Espresso Machine", 399.99),
            ("PROD-017", "Air Fryer Pro XL", 149.99),
            ("PROD-018", "Stainless Steel Cookware Set", 189.99),
            ("PROD-019", "Vacuum Insulated Tumbler", 24.99),
            ("PROD-020", "Robotic Vacuum Cleaner", 299.99),
        ],
        "Audio": [
            ("PROD-021", "Studio Reference Monitors", 279.99),
            ("PROD-022", "USB Condenser Microphone", 99.99),
            ("PROD-023", "Audiophile DAC/Amp", 159.99),
            ("PROD-024", "True Wireless Earbuds", 89.99),
            ("PROD-025", "Soundbar with Subwoofer", 219.99),
        ],
    }

    customers = [
        ("CUST-1001", "Emma Watson", "emma.w@example.com", "New York", "NY"),
        ("CUST-1002", "Liam Smith", "liam.smith@example.com", "Los Angeles", "CA"),
        ("CUST-1003", "Olivia Johnson", "olivia.j@example.com", "Chicago", "IL"),
        ("CUST-1004", "Noah Brown", "noah.b@example.com", "Houston", "TX"),
        ("CUST-1005", "Sophia Garcia", "sophia.g@example.com", "Phoenix", "AZ"),
        ("CUST-1006", "Lucas Miller", "lucas.m@example.com", "San Francisco", "CA"),
        ("CUST-1007", "Mia Davis", "mia.davis@example.com", "Seattle", "WA"),
        ("CUST-1008", "Ethan Martinez", "ethan.m@example.com", "Austin", "TX"),
        ("CUST-1009", "Isabella Rodriguez", "isabella.r@example.com", "Miami", "FL"),
        ("CUST-1010", "Aiden Wilson", "aiden.w@example.com", "Denver", "CO"),
        ("CUST-1011", "Harper Anderson", "harper.a@example.com", "Boston", "MA"),
        ("CUST-1012", "James Taylor", "james.t@example.com", "Atlanta", "GA"),
        ("CUST-1013", "Evelyn Thomas", "evelyn.t@example.com", "Portland", "OR"),
        ("CUST-1014", "Benjamin White", "ben.w@example.com", "Dallas", "TX"),
        ("CUST-1015", "Charlotte Harris", "charlotte.h@example.com", "San Diego", "CA"),
        ("CUST-1016", "Alexander Clark", "alex.c@example.com", "Minneapolis", "MN"),
        ("CUST-1017", "Amelia Lewis", "amelia.l@example.com", "Philadelphia", "PA"),
        ("CUST-1018", "Mason Lee", "mason.lee@example.com", "Charlotte", "NC"),
        ("CUST-1019", "Abigail Walker", "abigail.w@example.com", "Nashville", "TN"),
        ("CUST-1020", "Elijah Hall", "elijah.h@example.com", "Detroit", "MI"),
        ("CUST-1021", "Emily Allen", "emily.a@example.com", "Salt Lake City", "UT"),
        ("CUST-1022", "Logan Young", "logan.y@example.com", "Orlando", "FL"),
        ("CUST-1023", "Elizabeth King", "elizabeth.k@example.com", "Las Vegas", "NV"),
        ("CUST-1024", "Oliver Wright", "oliver.w@example.com", "Raleigh", "NC"),
        ("CUST-1025", "Avery Scott", "avery.s@example.com", "Kansas City", "MO"),
        ("CUST-1026", "Henry Green", "henry.g@example.com", "Indianapolis", "IN"),
        ("CUST-1027", "Ella Adams", "ella.a@example.com", "Columbus", "OH"),
        ("CUST-1028", "Sebastian Baker", "sebastian.b@example.com", "San Antonio", "TX"),
        ("CUST-1029", "Scarlett Gonzalez", "scarlett.g@example.com", "San Jose", "CA"),
        ("CUST-1030", "Jack Nelson", "jack.n@example.com", "Tampa", "FL"),
    ]

    # Additional repeat customer pool to demonstrate repeat purchase behavior
    all_customers = customers + [
        (f"CUST-{1030 + i}", f"Customer {i}", f"cust{i}@example.com", 
         random.choice(["New York", "Chicago", "San Francisco", "Austin", "Seattle"]),
         random.choice(["NY", "IL", "CA", "TX", "WA"]))
        for i in range(1, 51)
    ]

    all_products = []
    for cat, prod_list in categories.items():
        for p in prod_list:
            all_products.append((p[0], p[1], cat, p[2]))

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    delta_days = (end_date - start_date).days

    rows = []
    order_id_counter = 5001

    for _ in range(num_records):
        cust = random.choice(all_customers)
        prod = random.choice(all_products)
        random_days = random.randint(0, delta_days)
        order_date_obj = start_date + timedelta(days=random_days)

        # Quantity: mostly 1-5, occasionally higher
        qty = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[50, 25, 12, 6, 4, 2, 1])[0]
        price = prod[3]

        # Introduce deliberate raw anomalies for ~8% of records:
        anomaly_type = random.choices(
            ["none", "dirty_price", "negative_qty", "null_customer", "mixed_date", "dirty_category"],
            weights=[82, 4, 3, 3, 5, 3]
        )[0]

        order_id_str = f"ORD-{order_id_counter}"
        order_id_counter += 1

        cust_id = cust[0]
        cust_name = cust[1]
        cust_email = cust[2]
        cust_city = cust[3]
        cust_state = cust[4]

        prod_id = prod[0]
        prod_name = prod[1]
        prod_cat = prod[2]

        price_str = f"{price:.2f}"
        qty_str = str(qty)

        # Date formatting variations
        date_format_choice = random.choice(["iso", "slash_us", "slash_eur", "dash_short"])
        if date_format_choice == "iso":
            date_str = order_date_obj.strftime("%Y-%m-%d")
        elif date_format_choice == "slash_us":
            date_str = order_date_obj.strftime("%m/%d/%Y")
        elif date_format_choice == "slash_eur":
            date_str = order_date_obj.strftime("%d/%m/%Y")
        else:
            date_str = order_date_obj.strftime("%Y/%m/%d")

        # Inject anomalies
        if anomaly_type == "dirty_price":
            price_str = f"${price:,.2f} "  # currency symbol and trailing space
        elif anomaly_type == "negative_qty":
            qty_str = str(-qty)  # negative quantity
        elif anomaly_type == "null_customer":
            cust_name = ""  # missing customer name
            cust_id = ""    # missing customer id
        elif anomaly_type == "mixed_date":
            date_str = f"  {order_date_obj.strftime('%b %d, %Y')}  " # unpadded text date
        elif anomaly_type == "dirty_category":
            prod_cat = prod_cat.upper() if random.random() > 0.5 else prod_cat.lower()

        rows.append({
            "order_id": order_id_str,
            "order_date": date_str,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "customer_email": cust_email,
            "customer_city": cust_city,
            "customer_state": cust_state,
            "product_id": prod_id,
            "product_name": prod_name,
            "category": prod_cat,
            "quantity": qty_str,
            "unit_price": price_str,
            "order_status": random.choice(["Delivered", "Delivered", "Delivered", "Shipped", "Cancelled"])
        })

    # Add deliberate duplicate records (~40 rows)
    num_duplicates = 40
    for _ in range(num_duplicates):
        dup_row = dict(random.choice(rows))
        rows.append(dup_row)

    # Shuffle to distribute duplicates
    random.shuffle(rows)

    fieldnames = [
        "order_id", "order_date", "customer_id", "customer_name", "customer_email",
        "customer_city", "customer_state", "product_id", "product_name", "category",
        "quantity", "unit_price", "order_status"
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {len(rows)} raw sales records at: {output_path}")

if __name__ == "__main__":
    generate_raw_sales_data()
