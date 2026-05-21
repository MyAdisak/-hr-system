# Database Schema

PostgreSQL database: `hr_system`

## Schemas

| Schema | Purpose |
|------|-------|
| `n8n` | n8n internal (workflows, credentials, executions) |
| `public` | HR application data |

## HR Tables (public) - 13 tables

| Table | Description |
|------|-----------|
| `employees` | บริษั พนักงาน (LINE user ID) |
| `departments` | แผนกยื่ |
| `leave_requests` | คำขอลา |
| `attendance` | บันทึกเข้าออก |
| `payroll` | เงินเดือน |
| `salary_advances` | เบิกเงินล่วงหน้า |
| `advance_repayments` | หักเงินคืน |
| `chat_sessions` | context chatbot |
| `admin_notes` | บันทึก Admin |
| `factory_shipments` | สินค้าออก |
| `shipment_items` | items ใน shipment |
| `petty_expenses` | ค่าใช้จ่ายปลีกย่อย |
| `petty_expense_items` | items |

## ดู Schema

```bash
docker exec hr_postgres psql -U postgres -d hr_system -c "\dt public.*"

docker exec hr_postgres psql -U postgres -d hr_system -c "\d public.employees"
```

## ตัวอย่าง Query

```sql
SELECT emp_id, full_name, position
FROM employees
WHERE dept_id = 1 AND status = 'active';

SELECT lr.*, e.full_name
FROM leave_requests lr
JOIN employees e ON lr.emp_id = e.emp_id
WHERE lr.start_date >= CURRENT_DATE - INTERVAL '30 days';

SELECT COUNT(*) AS today_checkins
FROM attendance
WHERE work_date = CURRENT_DATE;
```
