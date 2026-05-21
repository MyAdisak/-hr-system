-- HR System schema
-- Runs only on first PostgreSQL initialization when ./postgres/data is empty.

CREATE TABLE IF NOT EXISTS departments (
  dept_id SERIAL PRIMARY KEY,
  dept_name VARCHAR(100) NOT NULL UNIQUE,
  manager_id INT,
  line_group_id VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employees (
  emp_id SERIAL PRIMARY KEY,
  line_user_id VARCHAR(100) UNIQUE,
  emp_code VARCHAR(20) UNIQUE NOT NULL,
  full_name VARCHAR(200) NOT NULL,
  dept_id INT REFERENCES departments(dept_id),
  position VARCHAR(100),
  role VARCHAR(20) DEFAULT 'employee' CHECK (role IN ('employee','manager','admin','hr')),
  hire_date DATE,
  base_salary NUMERIC(12,2) DEFAULT 0,
  daily_wage NUMERIC(12,2) DEFAULT 0,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active','inactive')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS leave_requests (
  leave_id SERIAL PRIMARY KEY,
  emp_id INT NOT NULL REFERENCES employees(emp_id),
  leave_type VARCHAR(20) NOT NULL CHECK (leave_type IN ('sick','annual','personal','other')),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_days INT NOT NULL,
  reason TEXT,
  status VARCHAR(20) DEFAULT 'approved' CHECK (status IN ('pending','approved','rejected')),
  approved_by INT REFERENCES employees(emp_id),
  approved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS attendance (
  att_id SERIAL PRIMARY KEY,
  emp_id INT NOT NULL REFERENCES employees(emp_id),
  work_date DATE NOT NULL,
  check_in TIMESTAMP,
  check_out TIMESTAMP,
  ot_minutes INT DEFAULT 0,
  location_lat NUMERIC(10,7),
  location_lng NUMERIC(10,7),
  method VARCHAR(20) DEFAULT 'line' CHECK (method IN ('line','qr','manual','fingerprint')),
  status VARCHAR(20) DEFAULT 'normal' CHECK (status IN ('normal','late','absent','leave')),
  UNIQUE(emp_id, work_date)
);

CREATE TABLE IF NOT EXISTS salary_advances (
  advance_id SERIAL PRIMARY KEY,
  emp_id INT NOT NULL REFERENCES employees(emp_id),
  advance_date DATE NOT NULL DEFAULT CURRENT_DATE,
  amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
  note TEXT,
  deduct_period VARCHAR(7) NOT NULL,
  deduct_status VARCHAR(20) DEFAULT 'pending' CHECK (deduct_status IN ('pending','deducted')),
  recorded_by INT REFERENCES employees(emp_id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payroll (
  payroll_id SERIAL PRIMARY KEY,
  emp_id INT NOT NULL REFERENCES employees(emp_id),
  pay_period VARCHAR(7) NOT NULL,
  base_salary NUMERIC(12,2) DEFAULT 0,
  work_days NUMERIC(8,2) DEFAULT 0,
  ot_pay NUMERIC(12,2) DEFAULT 0,
  allowances NUMERIC(12,2) DEFAULT 0,
  advance_deduction NUMERIC(12,2) DEFAULT 0,
  other_deductions NUMERIC(12,2) DEFAULT 0,
  tax NUMERIC(12,2) DEFAULT 0,
  net_pay NUMERIC(12,2) GENERATED ALWAYS AS
    (base_salary + ot_pay + allowances - advance_deduction - other_deductions - tax) STORED,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(emp_id, pay_period)
);

CREATE TABLE IF NOT EXISTS advance_repayments (
  repay_id SERIAL PRIMARY KEY,
  advance_id INT NOT NULL REFERENCES salary_advances(advance_id),
  emp_id INT NOT NULL REFERENCES employees(emp_id),
  pay_period VARCHAR(7) NOT NULL,
  deduct_amount NUMERIC(12,2) NOT NULL CHECK (deduct_amount > 0),
  recorded_by INT REFERENCES employees(emp_id),
  deducted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id SERIAL PRIMARY KEY,
  line_user_id VARCHAR(100) NOT NULL UNIQUE,
  state VARCHAR(100),
  intent VARCHAR(100),
  context JSONB DEFAULT '{}'::jsonb,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_notes (
  note_id SERIAL PRIMARY KEY,
  note_date DATE DEFAULT CURRENT_DATE,
  category VARCHAR(50) DEFAULT 'ทั่วไป',
  title VARCHAR(200),
  content TEXT NOT NULL,
  tags JSONB DEFAULT '[]'::jsonb,
  is_pinned BOOLEAN DEFAULT FALSE,
  created_by INT REFERENCES employees(emp_id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_notes_fts
ON admin_notes USING gin(to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,'')));

CREATE TABLE IF NOT EXISTS factory_shipments (
  shipment_id SERIAL PRIMARY KEY,
  shipment_date DATE NOT NULL DEFAULT CURRENT_DATE,
  ref_no VARCHAR(100),
  destination VARCHAR(200),
  total_weight_kg NUMERIC(12,3) DEFAULT 0,
  total_amount NUMERIC(14,2) DEFAULT 0,
  note TEXT,
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft','confirmed','shipped')),
  created_by INT REFERENCES employees(emp_id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shipment_items (
  item_id SERIAL PRIMARY KEY,
  shipment_id INT NOT NULL REFERENCES factory_shipments(shipment_id) ON DELETE CASCADE,
  product_name VARCHAR(200) NOT NULL,
  product_code VARCHAR(50),
  unit VARCHAR(30),
  quantity NUMERIC(12,3) NOT NULL DEFAULT 0,
  weight_per_unit NUMERIC(10,4) DEFAULT 0,
  total_weight NUMERIC(12,3) DEFAULT 0,
  price_per_unit NUMERIC(12,2) DEFAULT 0,
  total_price NUMERIC(14,2) DEFAULT 0,
  note TEXT
);

CREATE TABLE IF NOT EXISTS petty_expenses (
  expense_id SERIAL PRIMARY KEY,
  expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
  ref_no VARCHAR(100),
  dept_id INT REFERENCES departments(dept_id),
  total_amount NUMERIC(14,2) DEFAULT 0,
  note TEXT,
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft','submitted','approved','rejected')),
  approved_by INT REFERENCES employees(emp_id),
  approved_at TIMESTAMP,
  created_by INT REFERENCES employees(emp_id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS petty_expense_items (
  ei_id SERIAL PRIMARY KEY,
  expense_id INT NOT NULL REFERENCES petty_expenses(expense_id) ON DELETE CASCADE,
  description VARCHAR(300) NOT NULL,
  category VARCHAR(80),
  quantity NUMERIC(10,3) DEFAULT 1,
  unit VARCHAR(30),
  unit_price NUMERIC(12,2) DEFAULT 0,
  amount NUMERIC(14,2) DEFAULT 0,
  receipt_img TEXT,
  note TEXT
);

CREATE INDEX IF NOT EXISTS idx_emp_line ON employees(line_user_id);
CREATE INDEX IF NOT EXISTS idx_emp_code ON employees(emp_code);
CREATE INDEX IF NOT EXISTS idx_att_emp_date ON attendance(emp_id, work_date);
CREATE INDEX IF NOT EXISTS idx_leave_emp ON leave_requests(emp_id, start_date);
CREATE INDEX IF NOT EXISTS idx_advance_pending ON salary_advances(deduct_status, deduct_period);
CREATE INDEX IF NOT EXISTS idx_session_uid ON chat_sessions(line_user_id, updated_at);

INSERT INTO departments (dept_name)
VALUES ('ฝ่ายบุคคล'), ('ฝ่ายผลิต'), ('ฝ่ายบัญชี')
ON CONFLICT (dept_name) DO NOTHING;
