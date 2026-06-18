ETL Pipeline — mosmusic_dwh

Описание проекта
End-to-end ETL-пайплайн для загрузки данных из разных источников (CSV, JSON, XLSX, XML) в PostgreSQL с аналитическими SQL-запросами.

Данные содержат информацию о клиентах, заказах, товарах, платежах и событиях пользовательской активности.

Структура проекта: 

block3/
├── src/
│   └── etl.py              # ETL-скрипт
├── sql/
│   └── analytics.sql       # Аналитические запросы
├── ddl/
│   └── create_tables.sql   # DDL: создание таблиц
├── data/
│   ├── customers.csv
│   ├── orders.json
│   ├── products.xlsx
│   ├── payments.csv
│   └── events.xml
├── .env                    # Конфигурация подключения к БД (не коммитится!)
├── .env.example            # Пример конфигурации
├── requirements.txt        # Зависимости
└── README.md               # Документация


Стек технологий
Python 3.10+
pandas, openpyxl, lxml — обработка данных
SQLAlchemy + psycopg2 — работа с PostgreSQL
python-dotenv — управление переменными окружения
PostgreSQL — хранилище данных


Установка и настройка
1. Клонируйте репозиторий
bash
git clone <repository-url>
cd block3

2. Создайте и активируйте виртуальное окружение
# Windows
python -m venv .venv
.venv\Scripts\activate
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

3. Установите зависимости
pip install -r requirements.txt

4. Настройте подключение к базе данных
Создайте файл .env в корне проекта на основе .env.example:
cp .env.example .env
Отредактируйте .env и укажите свои параметры подключения:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=mosmusic_dwh
DB_USER=your_username
DB_PASSWORD=your_password


5. Создайте базу данных и таблицы
-- Создайте базу данных в PostgreSQL
CREATE DATABASE mosmusic_dwh;

-- Выполните DDL скрипт для создания таблиц
-- Откройте ddl/create_tables.sql в DBeaver/psql и выполните


6. Запустите ETL
python src/etl.py


7. Выполните аналитические запросы
Откройте sql/analytics.sql в DBeaver и выполните запросы для анализа данных.

Архитектурные решения
Модель данных — Star Schema
Таблицы фактов: orders, payments, events
Таблицы измерений: customers, products


Data Quality & Обработка ошибок
Дубликаты: удаляются через drop_duplicates() по первичному ключу
Невалидные даты (например, 2025-99-99): заменяются на NULL
Некорректные ключи (BAD_ID, пустые значения): фильтруются
Телефоны со значением UNKNOWN: заменяются на NULL
Неактивные товары (is_active = False): логируются в error_log
Все проблемные записи: сохраняются в data/error_log.csv с указанием:
- источника данных
- идентификатора записи
- причины ошибки
- временной метки


Безопасность
Пароль и параметры подключения вынесены в .env файл
.env добавлен в .gitignore — конфиденциальные данные не попадают в репозиторий
Пример конфигурации в .env.example для быстрой настройки



Аналитические запросы (sql/analytics.sql)
Доступны следующие аналитические отчёты:
- Топ клиентов по сумме заказов
- Выручка по месяцам
- Самые популярные товары
- Последняя активность пользователей
- Пользователи без заказов


Воспроизведение результата
- Выполните шаги из раздела "Установка и настройка"
- Убедитесь, что ETL завершился успешно:

✅ Подключение к БД успешно!
Таблицы очищены
=== Загрузка customers ===
  Загружено строк: XXX
...
✓ ETL завершён успешно!

- Проверьте лог ошибок (если есть): data/error_log.csv
- Откройте sql/analytics.sql в DBeaver
- Выполните запросы для получения аналитики