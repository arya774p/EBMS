# Page 1

<div align="center">

# MAHATMA JYOTIBA PHULE ROHILKHAND UNIVERSITY, BAREILLY - 243006

## 2023-2027

# PROJECT REPORT

## ON

# "ELECTRICITY BILL MANAGEMENT SYSTEM"

## DEPARTMENT OF COMPUTER SCIENCE AND INFORMATION TECHNOLOGY

### SUBMITTED TO:

**DR. SUSHEEL GANGWAR SIR**

### SUBMITTED BY:

- **Student Name 1** (Roll No.)
- **Student Name 2** (Roll No.)
- **Student Name 3** (Roll No.)
- **Student Name 4** (Roll No.)

</div>

---

# Page 2

# TABLE OF CONTENTS

1. **Acknowledgement** ................................................................................ 4  
2. **Introduction** ........................................................................................ 5  
3. **Problem with the Current System** .................................................... 5  
   1. Manual Bill Generation  
   2. Poor Record Management  
   3. Delayed Meter Request Handling  
   4. Inefficient Reading Management  
   5. Limited Customer Access  
   6. Payment Tracking Issues  
   7. Difficulty in Report Generation  
   8. Lack of Transaction Safety  
4. **Objectives** .......................................................................................... 6  
5. **ER Diagram Description** .................................................................... 7  
6. **Entities and Their Attributes** ............................................................ 8  
   1. Customer  
   2. App User  
   3. Address  
   4. Meter Request  
   5. Meter  
   6. Reading  
   7. Bill  
   8. Payment  
   9. SQL Query Log  

---

# Page 3

# TABLE OF CONTENTS

7. **Relationships** ..................................................................................... 10  
8. **Database Schema and SQL Queries** .................................................. 11  
   1. Creating Database  
   2. Creating Tables  
   3. Creating View  
   4. Sample Insert Queries  
9. **DBMS Concepts Used in the Project** ................................................. 13  
10. **Future Advancements** ...................................................................... 14  
    1. Online Payment Gateway Integration  
    2. PDF Bill Download  
    3. Email and SMS Notifications  
    4. Smart Meter Integration  
    5. Advanced Analytics Dashboard  
    6. Mobile Application Support  
    7. Complaint Management  
    8. Role-Based Audit Reports  
    9. Backup and Recovery Module  
    10. Multi-Language Interface  
11. **References** ........................................................................................ 15  

---

# Page 4

# ACKNOWLEDGEMENT

We would like to express our sincere gratitude to our project guide, **Dr. Susheel Gangwar Sir**, for guiding us throughout the development of our DBMS project. His suggestions helped us understand how a database application should be designed in a practical and structured way.

We are also thankful to the Department of Computer Science and Information Technology for providing us with the opportunity to work on this project. This project helped us connect classroom DBMS concepts with a real-world application.

During the development of the Electricity Bill Management System, we learned how tables are connected using primary keys and foreign keys, how transactions protect data, and how a web application communicates with a MySQL database. We also understood the importance of validations, secure login, role-based access, and proper record management.

Lastly, we would like to thank our teammates, friends, and family members for their support and encouragement. Their motivation helped us complete this project with dedication and teamwork.

---

# Page 5

# ELECTRICITY BILL MANAGEMENT SYSTEM

# INTRODUCTION

Electricity billing is an important part of power distribution management. In a traditional system, customer details, meter requests, meter readings, bills, and payments are often handled manually or with separate records. This can create confusion, delays, calculation mistakes, and difficulty in tracking customer history.

The **Electricity Bill Management System (EBMS)** is a web-based DBMS project developed using **Flask, MySQL, SQLAlchemy, HTML, and Tailwind CSS**. The system is designed to manage the complete flow of electricity billing, starting from customer registration to bill payment.

In this system, customers can sign up, manage their profile, add addresses, request a new meter, view meter status, check bills, and make payments. Admin users can approve or reject meter requests, create meters, add meter readings, generate bills, update bill status, and view payment records.

The project is especially useful as a DBMS course project because it uses relational database concepts in a practical manner. It includes normalized tables, primary keys, foreign keys, unique constraints, views, joins, transactions, commit, rollback, and SQL query logging.

# PROBLEM WITH THE CURRENT SYSTEM

In many electricity billing setups, work is still dependent on manual registers or disconnected software. This creates several problems for both customers and administrators.

## 1. Manual Bill Generation

Bills are often calculated manually from meter readings. This increases the chances of calculation errors and makes the process slow.

## 2. Poor Record Management

Customer details, addresses, meter information, readings, bills, and payments may be stored in different places. Searching old records becomes difficult and time-consuming.

---

# Page 6

# PROBLEM WITH THE CURRENT SYSTEM

## 3. Delayed Meter Request Handling

When a customer applies for a new electricity meter, approval may take time because the request is not tracked properly. Customers also do not get a clear status update.

## 4. Inefficient Reading Management

Meter readings must be stored carefully because each bill depends on previous and current readings. Manual systems do not properly prevent duplicate or inconsistent readings.

## 5. Limited Customer Access

Customers usually have to visit an office or contact staff to check bills, meter status, or payment history. This increases dependency on administrative staff.

## 6. Payment Tracking Issues

Manual payment records can lead to confusion about whether a bill is paid, pending, failed, or refunded.

## 7. Difficulty in Report Generation

Without a proper database system, generating reports for customers, bills, payments, and meter requests becomes difficult.

## 8. Lack of Transaction Safety

Important operations like approving a meter request or paying a bill affect multiple tables. If one step fails and there is no rollback mechanism, the database can contain incomplete or incorrect data.

# OBJECTIVES

## 1. Customer Registration and Login

To allow customers and admins to securely login using role-based authentication.

## 2. Customer Profile Management

To allow customers to view and update their basic profile details such as name and phone number.

## 3. Address Management

To allow customers to add, edit, and delete addresses linked to their account.

---

# Page 7

# OBJECTIVES

## 4. Meter Request Management

To allow customers to request a new electricity meter and track whether the request is pending, approved, rejected, or cancelled.

## 5. Admin Approval System

To allow admins to approve or reject meter requests. When a request is approved, a new meter is created automatically.

## 6. Meter and Reading Management

To allow admins to manage meters and add meter readings. The system validates readings to avoid duplicate or inconsistent values.

## 7. Bill Generation

To generate electricity bills from meter readings using simple slab-based billing rules for domestic and commercial categories.

## 8. Payment Management

To allow customers to pay bills and allow admins to view all payment records.

## 9. DBMS Concept Demonstration

To demonstrate relational database concepts such as keys, joins, views, constraints, transactions, commit, rollback, and query logging.

## 10. Better User Interface

To provide a clean and simple interface for customers and admins using Flask templates and Tailwind CSS.

# ER DIAGRAM DESCRIPTION

The Electricity Bill Management System is based on a relational database design. The main entities of the system are **Customer, App User, Address, Meter Request, Meter, Reading, Bill, Payment, and SQL Query Log**.

The customer is the central entity. A customer can have multiple addresses, multiple meter requests, and multiple meters. Each meter belongs to one customer and one address. Readings are stored for each meter, and bills are generated using previous and current readings. Payments are linked to bills.

The SQL Query Log table is added to make the project more relevant to DBMS. It stores executed SQL statements, route information, user role, execution time, and success or failure status.

---

# Page 8

# ENTITIES AND THEIR ATTRIBUTES

## 1. CUSTOMER

This entity stores the basic information of customers registered in the system.

**Primary Key:** `id`  
**Unique Key:** `account_no`

**Attributes:**

- `id`: Uniquely identifies each customer.
- `account_no`: Unique account number generated for every customer.
- `full_name`: Full name of the customer.
- `phone`: Customer contact number.
- `created_at`: Date and time when the customer record was created.
- `updated_at`: Date and time when customer details were last updated.

## 2. APP_USER

This entity stores login details and role information.

**Primary Key:** `id`  
**Unique Key:** `email`  
**Foreign Key:** `customer_id` references `customer(id)`

**Attributes:**

- `id`: Uniquely identifies each user account.
- `email`: Email used for login.
- `password_hash`: Encrypted password.
- `role`: Defines whether the user is `ADMIN` or `CUSTOMER`.
- `customer_id`: Links a customer user with the customer table.
- `is_active`: Shows whether the account is active.
- `created_at`: Date and time when the user account was created.

## 3. ADDRESS

This entity stores customer address details.

**Primary Key:** `id`  
**Foreign Key:** `customer_id` references `customer(id)`

**Attributes:**

- `id`: Uniquely identifies each address.
- `customer_id`: Identifies the customer who owns the address.
- `base_address`: House number, street, or main address line.
- `locality`: Local area name.
- `city`: City name.
- `state`: State name.
- `pincode`: Six digit pincode.
- `created_at`: Date and time when address was added.

---

# Page 9

# ENTITIES AND THEIR ATTRIBUTES

## 4. METER_REQUEST

This entity stores requests submitted by customers for new electricity meters.

**Primary Key:** `id`  
**Foreign Keys:** `customer_id`, `address_id`

**Attributes:**

- `id`: Uniquely identifies each meter request.
- `customer_id`: Customer who submitted the request.
- `address_id`: Address where the meter is required.
- `category`: Meter category, either `DOMESTIC` or `COMMERCIAL`.
- `sanction_load`: Approved load requested by the customer.
- `max_demand`: Maximum demand value, mainly useful for commercial meters.
- `request_status`: Current status such as pending, approved, rejected, or cancelled.
- `requested_at`: Date and time of request submission.
- `reviewed_at`: Date and time when admin reviewed the request.
- `admin_note`: Admin remark for approval or rejection.

## 5. METER

This entity stores approved meter details.

**Primary Key:** `id`  
**Unique Keys:** `meter_no`, `meter_request_id`  
**Foreign Keys:** `customer_id`, `address_id`, `meter_request_id`

**Attributes:**

- `id`: Uniquely identifies each meter.
- `customer_id`: Customer to whom meter belongs.
- `address_id`: Installation address.
- `meter_request_id`: Request from which meter was created.
- `meter_no`: Unique meter number.
- `category`: Domestic or commercial.
- `sanction_load`: Approved load.
- `max_demand`: Maximum demand.
- `status`: Active, disconnected, faulty, or inactive.
- `installation_date`: Date of meter installation.
- `disconnection_date`: Date of disconnection if applicable.

## 6. READING

This entity stores meter readings.

**Primary Key:** `id`  
**Foreign Key:** `meter_id` references `meter(id)`  
**Unique Constraint:** `meter_id`, `reading_date`

**Attributes:**

- `id`: Uniquely identifies each reading.
- `meter_id`: Meter for which reading is taken.
- `reading_date`: Date of reading.
- `reading_value`: Reading value in units.
- `reading_type`: Actual or estimated reading.

---

# Page 10

# ENTITIES AND THEIR ATTRIBUTES

## 7. BILL

This entity stores generated electricity bills.

**Primary Key:** `id`  
**Foreign Keys:** `meter_id`, `previous_reading_id`, `current_reading_id`  
**Unique Constraints:** `current_reading_id`, and `meter_id + billing_start + billing_end`

**Attributes:**

- `id`: Uniquely identifies each bill.
- `meter_id`: Meter for which bill is generated.
- `previous_reading_id`: Previous reading used for unit calculation.
- `current_reading_id`: Current reading used for unit calculation.
- `bill_generated_at`: Date and time of bill generation.
- `billing_start`: Start date of billing period.
- `billing_end`: End date of billing period.
- `due_date`: Last date for bill payment.
- `units_consumed`: Units consumed during the period.
- `gross_amount`: Bill amount before adjustments.
- `late_payment_surcharge`: Extra charge for late payment.
- `subsidy`: Subsidy amount.
- `advance_adjusted`: Advance amount adjusted.
- `status`: Generated, paid, overdue, or cancelled.

## 8. PAYMENT

This entity stores bill payment details.

**Primary Key:** `id`  
**Foreign Key:** `bill_id` references `bill(id)`

**Attributes:**

- `id`: Uniquely identifies each payment.
- `bill_id`: Bill for which payment is made.
- `payment_date`: Date and time of payment.
- `amount_paid`: Paid amount.
- `status`: Pending, completed, failed, or refunded.
- `payment_method`: UPI, debit card, credit card, or cash.
- `transaction_ref`: Transaction reference number.

## 9. SQL_QUERY_LOG

This entity records SQL statements executed by the application.

**Primary Key:** `id`  
**Foreign Key:** `user_id` references `app_user(id)`

It stores query text, parameters, route path, user role, execution duration, success status, and error message. This makes the project more useful for DBMS demonstration.

---

# Page 11

# RELATIONSHIPS

## 1. CUSTOMER - APP_USER

One customer has one user login account. The `customer_id` field in `app_user` connects login details with customer details.

## 2. CUSTOMER - ADDRESS

One customer can have multiple addresses. Each address belongs to only one customer.

## 3. CUSTOMER - METER_REQUEST

One customer can submit multiple meter requests. Each request belongs to one customer.

## 4. ADDRESS - METER_REQUEST

One address can be used in meter requests. A request is created for a particular address.

## 5. METER_REQUEST - METER

One approved request creates one meter. This relationship helps track which request resulted in which meter.

## 6. CUSTOMER - METER

One customer can have multiple meters. Each meter belongs to one customer.

## 7. METER - READING

One meter can have many readings. Each reading belongs to one meter.

## 8. READING - BILL

A bill uses two readings: previous reading and current reading. This helps calculate units consumed.

## 9. METER - BILL

One meter can have multiple bills. Each bill belongs to one meter.

## 10. BILL - PAYMENT

One bill can have payment records. When payment is completed, the bill status becomes paid.

# DATABASE SCHEMA AND SQL QUERIES

## Creating Database

```sql
CREATE DATABASE ebms;
USE ebms;
```

---

# Page 12

# CREATING TABLES

## Creating Table: CUSTOMER

```sql
CREATE TABLE customer (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    account_no CHAR(10) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Creating Table: APP_USER

```sql
CREATE TABLE app_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'CUSTOMER') NOT NULL,
    customer_id BIGINT UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);
```

## Creating Table: ADDRESS

```sql
CREATE TABLE address (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    base_address VARCHAR(255) NOT NULL,
    locality VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode CHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);
```

## Creating Table: METER_REQUEST

```sql
CREATE TABLE meter_request (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    address_id BIGINT NOT NULL,
    category ENUM('DOMESTIC', 'COMMERCIAL') NOT NULL,
    sanction_load DECIMAL(5,2) NOT NULL,
    max_demand DECIMAL(5,2),
    request_status ENUM('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED') DEFAULT 'PENDING',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    admin_note VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES address(id) ON DELETE RESTRICT
);
```

---

# Page 13

# CREATING TABLES AND VIEW

## Creating Table: METER

```sql
CREATE TABLE meter (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    address_id BIGINT NOT NULL,
    meter_request_id BIGINT UNIQUE,
    meter_no VARCHAR(20) UNIQUE NOT NULL,
    category ENUM('DOMESTIC', 'COMMERCIAL') NOT NULL,
    sanction_load DECIMAL(5,2) NOT NULL,
    max_demand DECIMAL(5,2),
    status ENUM('ACTIVE', 'DISCONNECTED', 'FAULTY', 'INACTIVE') DEFAULT 'ACTIVE',
    installation_date DATE NOT NULL,
    disconnection_date DATE NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES address(id) ON DELETE RESTRICT,
    FOREIGN KEY (meter_request_id) REFERENCES meter_request(id) ON DELETE SET NULL
);
```

## Creating Table: READING

```sql
CREATE TABLE reading (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    meter_id BIGINT NOT NULL,
    reading_date DATE NOT NULL,
    reading_value DECIMAL(12,2) NOT NULL,
    reading_type ENUM('ACTUAL', 'ESTIMATED') DEFAULT 'ACTUAL',
    UNIQUE (meter_id, reading_date),
    FOREIGN KEY (meter_id) REFERENCES meter(id) ON DELETE CASCADE
);
```

## Creating Table: BILL

```sql
CREATE TABLE bill (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    meter_id BIGINT NOT NULL,
    previous_reading_id BIGINT NOT NULL,
    current_reading_id BIGINT NOT NULL,
    bill_generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    billing_start DATE NOT NULL,
    billing_end DATE NOT NULL,
    due_date DATE NOT NULL,
    units_consumed DECIMAL(12,2) NOT NULL,
    gross_amount DECIMAL(12,2) NOT NULL,
    late_payment_surcharge DECIMAL(12,2) DEFAULT 0,
    subsidy DECIMAL(12,2) DEFAULT 0,
    advance_adjusted DECIMAL(12,2) DEFAULT 0,
    status ENUM('GENERATED', 'PAID', 'OVERDUE', 'CANCELLED') DEFAULT 'GENERATED'
);
```

## Creating View: BILL_SUMMARY

```sql
CREATE VIEW bill_summary AS
SELECT b.*,
CASE
    WHEN (gross_amount + late_payment_surcharge - subsidy - advance_adjusted) <= 0 THEN 0
    ELSE (gross_amount + late_payment_surcharge - subsidy - advance_adjusted)
END AS net_amount
FROM bill b;
```

---

# Page 14

# SAMPLE INSERT QUERIES AND DBMS CONCEPTS

## Inserting Customer

```sql
INSERT INTO customer (account_no, full_name, phone)
VALUES ('1000000001', 'Rahul Sharma', '9876543210');
```

## Inserting User Login

```sql
INSERT INTO app_user (email, password_hash, role, customer_id)
VALUES ('rahul@example.com', 'hashed_password_here', 'CUSTOMER', 1);
```

## Inserting Address

```sql
INSERT INTO address (customer_id, base_address, locality, city, state, pincode)
VALUES (1, 'House No. 21, Civil Lines', 'Near Main Market', 'Bareilly', 'Uttar Pradesh', '243001');
```

## Inserting Meter Request

```sql
INSERT INTO meter_request (customer_id, address_id, category, sanction_load, max_demand)
VALUES (1, 1, 'DOMESTIC', 2.00, NULL);
```

## Transaction Example: Approving Meter Request

```sql
START TRANSACTION;

UPDATE meter_request
SET request_status = 'APPROVED',
    reviewed_at = CURRENT_TIMESTAMP,
    admin_note = 'Approved after document verification'
WHERE id = 1 AND request_status = 'PENDING';

INSERT INTO meter (
    customer_id, address_id, meter_request_id, meter_no,
    category, sanction_load, max_demand, status, installation_date
)
SELECT customer_id, address_id, id, 'EBMS00000001',
       category, sanction_load, max_demand, 'ACTIVE', CURDATE()
FROM meter_request
WHERE id = 1;

COMMIT;
```

## Rollback Example

```sql
START TRANSACTION;

INSERT INTO payment (bill_id, amount_paid, status, payment_method)
VALUES (1, 500.00, 'COMPLETED', 'UPI');

ROLLBACK;
```

The rollback command cancels the insert operation, so the payment record is not saved.

---

# Page 15

# DBMS CONCEPTS USED IN THE PROJECT

The Electricity Bill Management System is designed not only as a web application but also as a proper DBMS project. The following concepts are used in the system:

## 1. Primary Key

Every table has a primary key such as `customer.id`, `meter.id`, and `bill.id`. This uniquely identifies every record.

## 2. Foreign Key

Foreign keys connect related tables. For example, `meter.customer_id` references `customer.id`, and `payment.bill_id` references `bill.id`.

## 3. Unique Constraint

Fields like `account_no`, `email`, and `meter_no` are unique so duplicate records cannot be created.

## 4. Views

The `bill_summary` view calculates net bill amount using gross amount, surcharge, subsidy, and advance adjustment.

## 5. Joins

Joins are used to display combined data such as customer name, meter number, bill amount, and payment status.

```sql
SELECT c.full_name, m.meter_no, b.id AS bill_id, bs.net_amount, b.status
FROM customer c
JOIN meter m ON m.customer_id = c.id
JOIN bill b ON b.meter_id = m.id
JOIN bill_summary bs ON bs.id = b.id;
```

## 6. Transactions

Transactions are used for important operations like meter approval, bill generation, and payment. If any step fails, rollback keeps the database safe.

## 7. SQL Query Logging

The `sql_query_log` table records SQL queries executed by the application. This helps in understanding how the Flask application communicates with MySQL.

# FUTURE ADVANCEMENTS

## 1. Online Payment Gateway Integration

In the future, the system can be connected with real payment gateways like UPI, Razorpay, or cards for live bill payment.

## 2. PDF Bill Download

Customers can be allowed to download their electricity bills in PDF format.

---

# Page 16

# FUTURE ADVANCEMENTS

## 3. Email and SMS Notifications

The system can send automatic notifications for bill generation, due date reminders, and successful payment confirmation.

## 4. Smart Meter Integration

Smart meters can be connected so that readings are automatically fetched without manual entry.

## 5. Advanced Analytics Dashboard

Admin dashboards can show graphs for monthly revenue, unpaid bills, highest consumption customers, and category-wise usage.

## 6. Mobile Application Support

A mobile app can be developed for customers so they can view bills and make payments from their phones.

## 7. Complaint Management

A complaint module can be added for meter faults, billing issues, and electricity supply problems.

## 8. Role-Based Audit Reports

The system can provide detailed reports showing which admin performed which action and when.

## 9. Backup and Recovery Module

Automatic database backup can be added to prevent data loss.

## 10. Multi-Language Interface

The system can support Hindi and other regional languages so that more users can access it easily.

# REFERENCES

- https://www.geeksforgeeks.org/dbms/
- https://flask.palletsprojects.com/
- https://flask-sqlalchemy.palletsprojects.com/
- https://dev.mysql.com/doc/
- https://tailwindcss.com/docs/installation/play-cdn
- Class notes and DBMS lab exercises

