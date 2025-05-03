
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;
SELECT pg_reload_conf();

SHOW wal_level;
SHOW max_replication_slots;
SHOW max_wal_senders;

CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(40),
    address TEXT
);

CREATE TABLE Credit_History (
    history_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id),
    bank_name VARCHAR(100),
    credit_score INT,
    outstanding_debt FLOAT,
    last_updated DATE
);

