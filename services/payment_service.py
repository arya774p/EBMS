from datetime import datetime

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Bill, Meter, Payment


PAYMENT_METHODS = {"UPI", "DEBIT_CARD", "CREDIT_CARD", "CASH"}
PAYMENT_STATUSES = {"PENDING", "COMPLETED", "FAILED", "REFUNDED"}


def pay_customer_bill(bill_id, customer_id, payment_method, transaction_ref=None):
    payment_method = payment_method if payment_method in PAYMENT_METHODS else "UPI"
    try:
        bill = (
            Bill.query.join(Meter)
            .filter(Bill.id == bill_id, Meter.customer_id == customer_id)
            .with_for_update()
            .first()
        )
        if not bill:
            raise ValueError("Bill was not found for your account.")
        if bill.status == "PAID":
            raise ValueError("This bill is already paid.")
        if bill.status == "CANCELLED":
            raise ValueError("Cancelled bills cannot be paid.")

        payment = Payment(
            bill_id=bill.id,
            amount_paid=bill.net_amount,
            status="COMPLETED",
            payment_method=payment_method,
            transaction_ref=transaction_ref or f"TXN{bill.id}{datetime.now():%Y%m%d%H%M%S}",
        )
        bill.status = "PAID"
        db.session.add(payment)
        db.session.commit()
        return payment
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Payment could not be saved.")
    except Exception:
        db.session.rollback()
        raise


def update_payment_status(payment_id, status):
    if status not in PAYMENT_STATUSES:
        raise ValueError("Invalid payment status.")

    try:
        payment = Payment.query.filter_by(id=payment_id).with_for_update().first()
        if not payment:
            raise ValueError("Payment was not found.")

        payment.status = status
        if status == "COMPLETED":
            payment.bill.status = "PAID"
        elif payment.bill.status == "PAID":
            payment.bill.status = "GENERATED"

        db.session.commit()
        return payment
    except Exception:
        db.session.rollback()
        raise
