<div align="center">

# mosmusic_DWH

### ETL-пайплайн и SQL-аналитика

Пять источников → очистка и преобразование → PostgreSQL → аналитические запросы.

**Python · pandas · SQLAlchemy · PostgreSQL**

</div>

---

## Задача

Объединить данные о клиентах, заказах, товарах, платежах и пользовательских событиях из файлов разных форматов в единой базе для дальнейшего анализа.

Проект демонстрирует загрузку данных, базовые проверки качества, журналирование ошибок и SQL-отчётность.

## Источники

| Файл | Формат | Содержание |
| :--- | :--- | :--- |
| `customers.csv` | CSV | Клиенты |
| `orders.json` | JSON | Заказы |
| `products.xlsx` | Excel | Товары |
| `payments.csv` | CSV, разделитель `^` | Платежи |
| `events.xml` | XML | Пользовательские события |

## Как устроена обработка

1. **Extract:** чтение пяти файлов из `data/`.
2. **Transform:** приведение названий столбцов и типов, обработка дат, удаление дубликатов и отдельных некорректных значений.
3. **Load:** загрузка в PostgreSQL через SQLAlchemy.
4. **Analyze:** SQL-запросы к загруженным таблицам.

## Качество данных

В [ETL-скрипте](src/etl.py) предусмотрены:

- удаление дубликатов по идентификаторам;
- преобразование некорректных дат в `NULL`;
- обработка нечисловых сумм платежей;
- исключение событий с нечисловым `event_id`;
- журналирование отсутствующих email, неактивных товаров и отдельных ошибок данных.

Журнал сохраняется в `data/error_log.csv`, если при запуске обнаружены ошибки. Состав проверок зависит от источника; это не полная система контроля качества.

## Аналитика

В [`sql/analytics.sql`](sql/analytics.sql) собраны примеры запросов:

- топ клиентов по сумме покупок;
- выручка по месяцам;
- количество заказов и дата последнего заказа;
- клиенты без заказов;
- пример запроса популярности товаров.

**Ограничение модели:** запрос популярности товаров использует сопоставление `orders.order_id = products.product_id`. В данных нет полноценной связи заказа с товаром, поэтому этот запрос требует доработки перед использованием для бизнес-выводов.

## Структура

```text
.
├── src/etl.py               # Чтение, очистка и загрузка
├── sql/analytics.sql        # Аналитические запросы
├── ddl/create_tables.sql    # Схема PostgreSQL
├── data/                   # Входные файлы и журнал ошибок
├── .env.example            # Шаблон подключения
├── .gitignore
├── requirements.txt
└── README.md
```

DDL создаёт таблицы `customers`, `products`, `orders`, `payments`, `events` и `fact_orders`. В текущем скрипте `fact_orders` очищается, но не заполняется.

## Запуск

Нужны Python 3.10+ и доступный сервер PostgreSQL.

### 1. Установка

```bash
git clone https://github.com/nagdarnik/etl-mosmusic-dwh.git
cd etl-mosmusic-dwh
python -m venv .venv
```

Активация окружения:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 2. Подключение

Скопируйте `.env.example` в `.env` и укажите параметры своей базы:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mosmusic_dwh
DB_USER=your_username
DB_PASSWORD=your_password
```

### 3. Создание схемы

Создайте базу `mosmusic_dwh`, затем выполните [`ddl/create_tables.sql`](ddl/create_tables.sql) в ней через psql, DBeaver или другой SQL-клиент.

```sql
CREATE DATABASE mosmusic_dwh;
```

### 4. Загрузка и анализ

**При каждом запуске ETL очищает целевые таблицы через `TRUNCATE ... CASCADE`. Используйте отдельную базу для проекта.**

```bash
python src/etl.py
```

После загрузки выполните нужные запросы из `sql/analytics.sql`. Если возникли ошибки преобразования данных, проверьте журнал `data/error_log.csv`.

## Автор

[Дарья Нагурная](https://github.com/nagdarnik) · Data Analytics / ETL
