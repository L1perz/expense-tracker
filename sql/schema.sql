-- Вариант 14. Все денежные величины хранятся целыми копейками.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0)
) STRICT;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    user_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    balance INTEGER NOT NULL CHECK (balance >= 0),
    UNIQUE (id, user_id)
) STRICT;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
) STRICT;

CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    user_id INTEGER NOT NULL REFERENCES users(id),
    account_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount INTEGER NOT NULL CHECK (amount > 0),
    date TEXT NOT NULL CHECK (
        length(date) = 10 AND date(date, '+0 days') IS NOT NULL
        AND date(date, '+0 days') = date
    ),
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    FOREIGN KEY (account_id, user_id) REFERENCES accounts(id, user_id)
) STRICT;

CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date);
CREATE INDEX IF NOT EXISTS idx_operations_account ON operations(account_id);
CREATE INDEX IF NOT EXISTS idx_operations_category ON operations(category_id);
CREATE INDEX IF NOT EXISTS idx_operations_user ON operations(user_id);
