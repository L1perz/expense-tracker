-- Эти именованные запросы выполняются db/repository.py и используются страницами.
-- Денежные параметры и результаты - в копейках. Месяц - ГГГГ-ММ или пустая строка.

-- name: users
-- 01. Список пользователей (SELECT, ORDER BY) -> /users/
SELECT id, name FROM users ORDER BY id;

-- name: categories
-- 02. Список категорий (SELECT, ORDER BY) -> /categories/
SELECT id, name FROM categories ORDER BY id;

-- name: accounts
-- 03. Счета с владельцами (JOIN) -> /accounts/ и главная
SELECT a.*, u.name AS user_name
FROM accounts AS a JOIN users AS u ON u.id = a.user_id ORDER BY a.id;

-- name: low_balance_accounts
-- 04. Фильтрация счетов по остатку (WHERE) -> /accounts/?max_balance=...
SELECT a.*, u.name AS user_name
FROM accounts AS a JOIN users AS u ON u.id = a.user_id
WHERE a.balance <= :max_balance ORDER BY a.balance, a.id;

-- name: account
-- 05. Карточка счёта (WHERE, JOIN) -> /accounts/<id>/
SELECT a.*, u.name AS user_name
FROM accounts AS a JOIN users AS u ON u.id = a.user_id WHERE a.id = :id;

-- name: operations
-- 06. История со всеми связанными сущностями (JOIN) -> /operations/
SELECT o.*, u.name AS user_name, a.name AS account_name, c.name AS category_name
FROM operations AS o
JOIN users AS u ON u.id = o.user_id
JOIN accounts AS a ON a.id = o.account_id
JOIN categories AS c ON c.id = o.category_id
ORDER BY o.date DESC, o.id DESC;

-- name: filtered_operations
-- 07. Пользовательский поиск по нескольким условиям (WHERE) -> /operations/?...
SELECT o.*, u.name AS user_name, a.name AS account_name, c.name AS category_name
FROM operations AS o
JOIN users AS u ON u.id = o.user_id
JOIN accounts AS a ON a.id = o.account_id
JOIN categories AS c ON c.id = o.category_id
WHERE (:month = '' OR substr(o.date, 1, 7) = :month)
  AND (:user_id IS NULL OR o.user_id = :user_id)
  AND (:category_id IS NULL OR o.category_id = :category_id)
  AND (:account_id IS NULL OR o.account_id = :account_id)
  AND instr(o.description, :query) > 0
ORDER BY o.date DESC, o.id DESC;

-- name: operation
-- 08. Карточка операции (WHERE, JOIN) -> /operations/<id>/
SELECT o.*, u.name AS user_name, a.name AS account_name, c.name AS category_name
FROM operations AS o
JOIN users AS u ON u.id = o.user_id
JOIN accounts AS a ON a.id = o.account_id
JOIN categories AS c ON c.id = o.category_id WHERE o.id = :id;

-- name: expense_summary
-- 09. Количество, сумма, минимум, максимум (агрегаты) -> обзор и статистика
SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total,
       COALESCE(MIN(amount), 0) AS minimum, COALESCE(MAX(amount), 0) AS maximum
FROM operations WHERE (:month = '' OR substr(date, 1, 7) = :month);

-- name: balance_summary
-- 10. Количество счетов и общий остаток (агрегаты) -> обзор
SELECT COUNT(*) AS account_count, COALESCE(SUM(balance), 0) AS balance FROM accounts;

-- name: category_totals
-- 11. Расходы по категориям (GROUP BY, HAVING) -> статистика
-- Условие месяца в ON сохраняет категории с нулём расходов.
SELECT c.id, c.name, COUNT(o.id) AS count, COALESCE(SUM(o.amount), 0) AS total
FROM categories AS c
LEFT JOIN operations AS o ON o.category_id = c.id
  AND (:month = '' OR substr(o.date, 1, 7) = :month)
GROUP BY c.id, c.name
HAVING COALESCE(SUM(o.amount), 0) >= :min_total
ORDER BY total DESC, c.id;

-- name: user_totals
-- 12. Расходы по пользователям, включая нулевые (GROUP BY) -> статистика
SELECT u.id, u.name, COUNT(o.id) AS count, COALESCE(SUM(o.amount), 0) AS total
FROM users AS u
LEFT JOIN operations AS o ON o.user_id = u.id
  AND (:month = '' OR substr(o.date, 1, 7) = :month)
GROUP BY u.id, u.name ORDER BY total DESC, u.id;

-- name: monthly_totals
-- 13. Динамика расходов по месяцам (GROUP BY) -> статистика
SELECT substr(date, 1, 7) AS month, COUNT(*) AS count, SUM(amount) AS total
FROM operations GROUP BY substr(date, 1, 7) ORDER BY month DESC;
