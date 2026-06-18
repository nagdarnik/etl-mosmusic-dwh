-- 1. Топ-10 клиентов по сумме покупок
SELECT
    c.name          AS customer,
    SUM(p.amount)   AS total_spent
FROM payments p
JOIN orders o   ON p.order_id   = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 10;


-- 2. Выручка по месяцам
SELECT
    TO_CHAR(paid_at, 'YYYY-MM') AS year_month,
    SUM(amount)                  AS revenue
FROM payments
WHERE paid_at IS NOT NULL
GROUP BY year_month
ORDER BY year_month;


-- 3. Самые популярные товары
SELECT
    p.name          AS product,
    p.category,
    COUNT(o.order_id) AS order_count
FROM orders o
JOIN products p ON o.order_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY order_count DESC
LIMIT 10;


-- 4. Последняя активность топ-5 пользователей по количеству покупок
SELECT
    c.name              AS customer,
    COUNT(o.order_id)   AS total_orders,
    MAX(o.created_at)   AS last_order_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_orders DESC
LIMIT 5;


-- 5. Пользователи без заказов
SELECT
    c.customer_id,
    c.name,
    c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;