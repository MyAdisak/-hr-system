CREATE USER n8n_user WITH PASSWORD 'giIfMy4Pvgs6tAop0Uh9dtej8sN0';

CREATE SCHEMA IF NOT EXISTS n8n AUTHORIZATION n8n_user;

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    line_user_id VARCHAR(100) UNIQUE,
    emp_code VARCHAR(20) UNIQUE,
    full_name VARCHAR(200),
    role VARCHAR(20) DEFAULT 'employee'
);

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    emp_id INT,
    work_date DATE,
    check_in TIMESTAMP,
    check_out TIMESTAMP
);

CREATE TABLE salary_advances (
    id SERIAL PRIMARY KEY,
    emp_id INT,
    amount NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);
