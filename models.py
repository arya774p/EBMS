from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from sqlalchemy import text

from extensions import db, login_manager


class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    account_no = db.Column(db.String(10), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship("AppUser", back_populates="customer", uselist=False)
    addresses = db.relationship("Address", back_populates="customer")
    meter_requests = db.relationship("MeterRequest", back_populates="customer")
    meters = db.relationship("Meter", back_populates="customer")


class AppUser(db.Model, UserMixin):
    __tablename__ = "app_user"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("ADMIN", "CUSTOMER"), nullable=False)
    customer_id = db.Column(
        db.BigInteger,
        db.ForeignKey("customer.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    customer = db.relationship("Customer", back_populates="user")


class Address(db.Model):
    __tablename__ = "address"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.BigInteger,
        db.ForeignKey("customer.id", ondelete="CASCADE"),
        nullable=False,
    )
    base_address = db.Column(db.String(255), nullable=False)
    locality = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    customer = db.relationship("Customer", back_populates="addresses")
    meter_requests = db.relationship("MeterRequest", back_populates="address")
    meters = db.relationship("Meter", back_populates="address")

    @property
    def display_line(self):
        parts = [self.base_address, self.locality, self.city, self.state, self.pincode]
        return ", ".join([part for part in parts if part])


class MeterRequest(db.Model):
    __tablename__ = "meter_request"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.BigInteger,
        db.ForeignKey("customer.id", ondelete="CASCADE"),
        nullable=False,
    )
    address_id = db.Column(
        db.BigInteger,
        db.ForeignKey("address.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category = db.Column(db.Enum("DOMESTIC", "COMMERCIAL"), nullable=False)
    sanction_load = db.Column(db.Numeric(5, 2), nullable=False)
    max_demand = db.Column(db.Numeric(5, 2))
    request_status = db.Column(
        db.Enum("PENDING", "APPROVED", "REJECTED", "CANCELLED"),
        default="PENDING",
    )
    requested_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime)
    admin_note = db.Column(db.String(255))

    customer = db.relationship("Customer", back_populates="meter_requests")
    address = db.relationship("Address", back_populates="meter_requests")
    meter = db.relationship("Meter", back_populates="meter_request", uselist=False)


class Meter(db.Model):
    __tablename__ = "meter"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.BigInteger,
        db.ForeignKey("customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    address_id = db.Column(
        db.BigInteger,
        db.ForeignKey("address.id", ondelete="RESTRICT"),
        nullable=False,
    )
    meter_request_id = db.Column(
        db.BigInteger,
        db.ForeignKey("meter_request.id", ondelete="SET NULL"),
        unique=True,
    )
    meter_no = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.Enum("DOMESTIC", "COMMERCIAL"), nullable=False)
    sanction_load = db.Column(db.Numeric(5, 2), nullable=False)
    max_demand = db.Column(db.Numeric(5, 2))
    status = db.Column(
        db.Enum("ACTIVE", "DISCONNECTED", "FAULTY", "INACTIVE"),
        default="ACTIVE",
    )
    installation_date = db.Column(db.Date, nullable=False)
    disconnection_date = db.Column(db.Date)

    customer = db.relationship("Customer", back_populates="meters")
    address = db.relationship("Address", back_populates="meters")
    meter_request = db.relationship("MeterRequest", back_populates="meter")
    readings = db.relationship(
        "Reading",
        back_populates="meter",
        order_by="Reading.reading_date.desc()",
    )
    bills = db.relationship("Bill", back_populates="meter", order_by="Bill.billing_end.desc()")


class Reading(db.Model):
    __tablename__ = "reading"
    __table_args__ = (db.UniqueConstraint("meter_id", "reading_date"),)

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    meter_id = db.Column(
        db.BigInteger,
        db.ForeignKey("meter.id", ondelete="CASCADE"),
        nullable=False,
    )
    reading_date = db.Column(db.Date, nullable=False)
    reading_value = db.Column(db.Numeric(12, 2), nullable=False)
    reading_type = db.Column(db.Enum("ACTUAL", "ESTIMATED"), default="ACTUAL")

    meter = db.relationship("Meter", back_populates="readings")
    current_bill = db.relationship(
        "Bill",
        back_populates="current_reading",
        foreign_keys="Bill.current_reading_id",
        uselist=False,
    )
    previous_bills = db.relationship(
        "Bill",
        back_populates="previous_reading",
        foreign_keys="Bill.previous_reading_id",
    )


class Bill(db.Model):
    __tablename__ = "bill"
    __table_args__ = (
        db.UniqueConstraint("current_reading_id"),
        db.UniqueConstraint("meter_id", "billing_start", "billing_end"),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    meter_id = db.Column(
        db.BigInteger,
        db.ForeignKey("meter.id", ondelete="RESTRICT"),
        nullable=False,
    )
    previous_reading_id = db.Column(
        db.BigInteger,
        db.ForeignKey("reading.id", ondelete="RESTRICT"),
        nullable=False,
    )
    current_reading_id = db.Column(
        db.BigInteger,
        db.ForeignKey("reading.id", ondelete="RESTRICT"),
        nullable=False,
    )
    bill_generated_at = db.Column(db.DateTime, default=datetime.now)
    billing_start = db.Column(db.Date, nullable=False)
    billing_end = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    units_consumed = db.Column(db.Numeric(12, 2), nullable=False)
    gross_amount = db.Column(db.Numeric(12, 2), nullable=False)
    late_payment_surcharge = db.Column(db.Numeric(12, 2), default=0)
    subsidy = db.Column(db.Numeric(12, 2), default=0)
    advance_adjusted = db.Column(db.Numeric(12, 2), default=0)
    status = db.Column(
        db.Enum("GENERATED", "PAID", "OVERDUE", "CANCELLED"),
        default="GENERATED",
    )

    meter = db.relationship("Meter", back_populates="bills")
    previous_reading = db.relationship(
        "Reading",
        foreign_keys=[previous_reading_id],
        back_populates="previous_bills",
    )
    current_reading = db.relationship(
        "Reading",
        foreign_keys=[current_reading_id],
        back_populates="current_bill",
    )
    payments = db.relationship("Payment", back_populates="bill", order_by="Payment.payment_date.desc()")

    @property
    def net_amount(self):
        gross = self.gross_amount or Decimal("0")
        surcharge = self.late_payment_surcharge or Decimal("0")
        subsidy = self.subsidy or Decimal("0")
        advance = self.advance_adjusted or Decimal("0")
        total = gross + surcharge - subsidy - advance
        return total if total > 0 else Decimal("0.00")


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    bill_id = db.Column(
        db.BigInteger,
        db.ForeignKey("bill.id", ondelete="CASCADE"),
        nullable=False,
    )
    payment_date = db.Column(db.DateTime, default=datetime.now)
    amount_paid = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(
        db.Enum("PENDING", "COMPLETED", "FAILED", "REFUNDED"),
        nullable=False,
    )
    payment_method = db.Column(
        db.Enum("UPI", "DEBIT_CARD", "CREDIT_CARD", "CASH"),
        nullable=False,
    )
    transaction_ref = db.Column(db.String(100))

    bill = db.relationship("Bill", back_populates="payments")


class SQLQueryLog(db.Model):
    __tablename__ = "sql_query_log"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    executed_at = db.Column(db.DateTime, server_default=text("CURRENT_TIMESTAMP"))
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("app_user.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_role = db.Column(db.String(20))
    route_path = db.Column(db.String(255))
    http_method = db.Column(db.String(10))
    statement_type = db.Column(db.String(20))
    query_text = db.Column(db.Text, nullable=False)
    parameters_json = db.Column(db.Text)
    duration_ms = db.Column(db.Numeric(10, 3))
    success = db.Column(db.Boolean, server_default=text("1"))
    error_message = db.Column(db.String(255))


@login_manager.user_loader
def load_user(user_id):
    return AppUser.query.get(int(user_id))
