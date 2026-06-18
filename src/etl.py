import os
from dotenv import load_dotenv
import pandas as pd
import json
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, text
from datetime import datetime
from pathlib import Path

# Определяем корневую директорию проекта
BASE_DIR = Path(__file__).parent.parent  # Поднимаемся на уровень выше от src/
DATA_DIR = BASE_DIR / 'data'

# Загрузка переменных из .env файла (он в корне)
load_dotenv(BASE_DIR / '.env')

# Получение параметров подключения из .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mosmusic_dwh')
DB_USER = os.getenv('DB_USER', 'nagdarnik')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Проверка наличия пароля
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD не найден в .env файле!")

# Формирование строки подключения
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание подключения
engine = create_engine(DB_URL)

# Проверка подключения
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Подключение к БД успешно!")
except Exception as e:
    print(f"❌ Ошибка подключения к БД: {e}")
    exit(1)

# Очистка таблиц
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE events, payments, orders, fact_orders, products, customers CASCADE"))
    conn.commit()
print("Таблицы очищены")

error_log = []

def log_error(source, row_id, reason):
    error_log.append({
        "source": source, 
        "row_id": row_id, 
        "reason": reason, 
        "logged_at": datetime.now().isoformat()
    })
    print(f"  [WARN] {source} | id={row_id} | {reason}")


# 1. CUSTOMERS
print("\n=== Загрузка customers ===")
df_customers = pd.read_csv(DATA_DIR / "customers.csv")
df_customers.loc[df_customers["phone"] == "UNKNOWN", "phone"] = None
df_customers["created_at"] = pd.to_datetime(df_customers["created_at"], errors="coerce")
for _, row in df_customers[df_customers["email"].isna()].iterrows():
    log_error("customers", row["customer_id"], "email is null")
df_customers = df_customers.rename(columns={"full_name": "name", "city": "country"})
df_customers = df_customers[["customer_id", "name", "email", "country", "created_at"]]
df_customers = df_customers.drop_duplicates(subset="customer_id")
df_customers.to_sql("customers", engine, if_exists="append", index=False)
print(f"  Загружено строк: {len(df_customers)}")


# 2. PRODUCTS
print("\n=== Загрузка products ===")
df_products = pd.read_excel(DATA_DIR / "products.xlsx")
for _, row in df_products[df_products["is_active"] == False].iterrows():
    log_error("products", row["product_id"], "product is inactive")
df_products = df_products.rename(columns={"product_name": "name"})
df_products = df_products[["product_id", "name", "category", "price"]]
df_products = df_products.drop_duplicates(subset="product_id")
df_products.to_sql("products", engine, if_exists="append", index=False)
print(f"  Загружено строк: {len(df_products)}")


# 3. ORDERS
print("\n=== Загрузка orders ===")
with open(DATA_DIR / "orders.json", encoding='utf-8') as f:
    raw_orders = json.load(f)
orders_clean = []
seen_orders = set()
for item in raw_orders:
    order_id = item.get("order_id")
    if order_id in seen_orders:
        continue
    seen_orders.add(order_id)
    try:
        ts = pd.to_datetime(item["order_timestamp"])
        if pd.isna(ts): 
            raise ValueError("NaT")
    except Exception:
        log_error("orders", order_id, f"invalid date: {item.get('order_timestamp')}")
        ts = None
    orders_clean.append({
        "order_id": order_id, 
        "customer_id": item.get("customer_id"), 
        "created_at": ts, 
        "status": item.get("status")
    })
df_orders = pd.DataFrame(orders_clean)
df_orders.to_sql("orders", engine, if_exists="append", index=False)
print(f"  Загружено строк: {len(df_orders)}")


# 4. PAYMENTS
print("\n=== Загрузка payments ===")
df_payments = pd.read_csv(DATA_DIR / "payments.csv", sep="^")
bad_amount = pd.to_numeric(df_payments["amount"], errors="coerce").isna()
for idx in df_payments[bad_amount].index:
    log_error("payments", df_payments.loc[idx, "payment_id"], f"invalid amount: {df_payments.loc[idx, 'amount']}")
df_payments["amount"] = pd.to_numeric(df_payments["amount"], errors="coerce")
df_payments = df_payments.rename(columns={"payment_timestamp": "paid_at", "payment_method": "method"})
df_payments["paid_at"] = pd.to_datetime(df_payments["paid_at"], errors="coerce")
df_payments = df_payments[["payment_id", "order_id", "amount", "paid_at", "method"]]
df_payments = df_payments.drop_duplicates(subset="payment_id")
df_payments.to_sql("payments", engine, if_exists="append", index=False)
print(f"  Загружено строк: {len(df_payments)}")


# 5. EVENTS
print("\n=== Загрузка events ===")
tree = ET.parse(DATA_DIR / "events.xml")
root = tree.getroot()
events_list = []
for el in root.findall("event"):
    events_list.append({
        "event_id": el.findtext("event_id"), 
        "customer_id": el.findtext("customer_id"), 
        "event_type": el.findtext("event_type"), 
        "happened_at": el.findtext("event_timestamp")
    })
df_events = pd.DataFrame(events_list)
df_events["happened_at"] = pd.to_datetime(df_events["happened_at"], errors="coerce")
df_events = df_events.drop_duplicates(subset="event_id")

# Фильтруем строки с невалидным event_id
bad_events = pd.to_numeric(df_events["event_id"], errors="coerce").isna()
for idx in df_events[bad_events].index:
    log_error("events", df_events.loc[idx, "event_id"], "invalid event_id")
df_events = df_events[~bad_events]
df_events["event_id"] = pd.to_numeric(df_events["event_id"])
df_events["customer_id"] = pd.to_numeric(df_events["customer_id"], errors="coerce")
df_events.to_sql("events", engine, if_exists="append", index=False)
print(f"  Загружено строк: {len(df_events)}")


# Сохранение лога ошибок
if error_log:
    pd.DataFrame(error_log).to_csv(DATA_DIR / "error_log.csv", index=False)
    print(f"\n=== Лог ошибок: {len(error_log)} записей → data/error_log.csv ===")

print("\n✓ ETL завершён успешно!")