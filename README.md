# Electricity Bill Management System

Flask + MySQL DBMS course project for customer electricity billing.

## Features

- Customer signup, login, logout, profile update
- Customer addresses, meter requests, meters, bills, and payments
- Admin dashboards, customers, approvals, meters, readings, bills, payments
- Admin SQL query log at `/admin/sql-queries`
- Bill generation from readings using simple slab rates

## DBMS Concepts Demonstrated

- Primary keys, unique keys, foreign keys, and enum constraints
- `ON DELETE CASCADE`, `RESTRICT`, and `SET NULL`
- Multi-table joins for customer, meter, bill, and payment views
- Aggregate dashboard queries
- `bill_summary` MySQL view for net amount
- Explicit `commit()` and `rollback()` in service functions
- Runtime SQL audit table: `sql_query_log`

## Admin Account

Create an admin from the terminal:

```powershell
$env:FLASK_APP="app:myapp"
flask create-admin --email admin@gmail.com
```

## DBMS Demo SQL

See `docs/dbms_queries.sql` for transaction, rollback, join, aggregate, view, constraint, and query-log examples.
