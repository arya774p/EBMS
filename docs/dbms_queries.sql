-- EBMS DBMS demonstration queries
-- Database name: ebms

USE ebms;

-- 1. Extra audit table added by the Flask app for SQL visibility.
CREATE TABLE IF NOT EXISTS sql_query_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT NULL,
    user_role VARCHAR(20),
    route_path VARCHAR(255),
    http_method VARCHAR(10),
    statement_type VARCHAR(20),
    query_text TEXT NOT NULL,
    parameters_json TEXT,
    duration_ms DECIMAL(10,3),
    success BOOLEAN DEFAULT TRUE,
    error_message VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE SET NULL
);

-- 2. Transaction + COMMIT example: approve one pending request manually.
START TRANSACTION;

UPDATE meter_request
SET request_status = 'APPROVED',
    reviewed_at = CURRENT_TIMESTAMP,
    admin_note = 'Approved from SQL demo'
WHERE id = 1
  AND request_status = 'PENDING';

INSERT INTO meter (
    customer_id, address_id, meter_request_id, meter_no, category,
    sanction_load, max_demand, status, installation_date
)
SELECT
    customer_id, address_id, id, CONCAT('SQLDEMO', id), category,
    sanction_load, max_demand, 'ACTIVE', CURDATE()
FROM meter_request
WHERE id = 1
  AND request_status = 'APPROVED';

COMMIT;

-- 3. Transaction + ROLLBACK example: test insert without saving.
START TRANSACTION;

INSERT INTO payment (bill_id, amount_paid, status, payment_method, transaction_ref)
VALUES (1, 500.00, 'COMPLETED', 'CASH', 'ROLLBACK-DEMO');

ROLLBACK;

-- 4. Join across customer, meter, bill, and payment.
SELECT
    c.account_no,
    c.full_name,
    m.meter_no,
    b.id AS bill_id,
    b.units_consumed,
    bs.net_amount,
    b.status AS bill_status,
    p.status AS payment_status
FROM customer c
JOIN meter m ON m.customer_id = c.id
JOIN bill b ON b.meter_id = m.id
JOIN bill_summary bs ON bs.id = b.id
LEFT JOIN payment p ON p.bill_id = b.id
ORDER BY b.bill_generated_at DESC;

-- 5. Dashboard aggregate queries.
SELECT COUNT(*) AS total_customers FROM customer;
SELECT request_status, COUNT(*) AS total FROM meter_request GROUP BY request_status;
SELECT status, COUNT(*) AS total FROM meter GROUP BY status;
SELECT status, COUNT(*) AS total, SUM(gross_amount) AS gross_total FROM bill GROUP BY status;
SELECT payment_method, COUNT(*) AS payments, SUM(amount_paid) AS amount FROM payment GROUP BY payment_method;

-- 6. View usage: net bill amount after surcharge, subsidy, and advance.
SELECT id, gross_amount, late_payment_surcharge, subsidy, advance_adjusted, net_amount
FROM bill_summary
ORDER BY bill_generated_at DESC;

-- 7. Constraint demonstration examples.
-- Unique constraint: account_no cannot repeat.
-- INSERT INTO customer (account_no, full_name, phone)
-- VALUES ('1234567890', 'Duplicate Account', '9999999999');

-- Foreign key constraint: bill_id must exist in bill.
-- INSERT INTO payment (bill_id, amount_paid, status, payment_method)
-- VALUES (999999, 100.00, 'COMPLETED', 'UPI');

-- Enum constraint: request_status must be one of the defined values.
-- UPDATE meter_request SET request_status = 'UNKNOWN' WHERE id = 1;

-- 8. Inspect SQL statements captured from the Flask app.
SELECT
    executed_at,
    user_role,
    route_path,
    statement_type,
    duration_ms,
    success,
    query_text
FROM sql_query_log
ORDER BY executed_at DESC
LIMIT 50;
