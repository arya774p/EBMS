from datetime import timedelta
from decimal import Decimal

from sqlalchemy import bindparam, text
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Bill, Reading
from utils.billing import calculate_bill_amount


def generate_bill_from_reading(current_reading_id):
    try:
        current_reading = (
            Reading.query.filter_by(id=current_reading_id)
            .with_for_update()
            .first()
        )
        if not current_reading:
            raise ValueError("Current reading was not found.")
        if Bill.query.filter_by(current_reading_id=current_reading.id).first():
            raise ValueError("A bill already exists for this reading.")

        previous_reading = (
            Reading.query.filter(
                Reading.meter_id == current_reading.meter_id,
                Reading.reading_date < current_reading.reading_date,
            )
            .order_by(Reading.reading_date.desc())
            .first()
        )
        if not previous_reading:
            raise ValueError("At least two readings are required. The first reading is only a baseline.")

        units = current_reading.reading_value - previous_reading.reading_value
        if units < Decimal("0"):
            raise ValueError("Current reading cannot be lower than the previous reading.")

        bill = Bill(
            meter_id=current_reading.meter_id,
            previous_reading_id=previous_reading.id,
            current_reading_id=current_reading.id,
            billing_start=previous_reading.reading_date,
            billing_end=current_reading.reading_date,
            due_date=current_reading.reading_date + timedelta(days=15),
            units_consumed=units.quantize(Decimal("0.01")),
            gross_amount=calculate_bill_amount(current_reading.meter.category, units),
            late_payment_surcharge=Decimal("0.00"),
            subsidy=Decimal("0.00"),
            advance_adjusted=Decimal("0.00"),
            status="GENERATED",
        )
        db.session.add(bill)
        db.session.commit()
        return bill
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Bill generation failed because this billing period already exists.")
    except Exception:
        db.session.rollback()
        raise


def bill_summary_map(bill_ids):
    ids = [int(bill_id) for bill_id in bill_ids]
    if not ids:
        return {}

    statement = text(
        "SELECT id, net_amount FROM bill_summary WHERE id IN :ids"
    ).bindparams(bindparam("ids", expanding=True))
    rows = db.session.execute(statement, {"ids": ids}).mappings().all()
    return {row["id"]: row["net_amount"] for row in rows}


def bill_net_amount(bill_id):
    row = db.session.execute(
        text("SELECT net_amount FROM bill_summary WHERE id = :bill_id"),
        {"bill_id": bill_id},
    ).first()
    return row[0] if row else Decimal("0.00")
