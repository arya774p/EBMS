from datetime import date

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Meter, Reading
from utils.forms import parse_date, parse_decimal


def add_meter_reading(meter_id, reading_date_value, reading_value, reading_type):
    reading_date = parse_date(reading_date_value, "Reading date")
    value = parse_decimal(reading_value, "Reading value", minimum=0)
    reading_type = reading_type if reading_type in {"ACTUAL", "ESTIMATED"} else "ACTUAL"

    try:
        meter = Meter.query.filter_by(id=meter_id).with_for_update().first()
        if not meter:
            raise ValueError("Meter was not found.")
        if meter.status != "ACTIVE":
            raise ValueError("Readings can be added only for active meters.")
        if reading_date < meter.installation_date:
            raise ValueError("Reading date cannot be before meter installation date.")
        if reading_date > date.today():
            raise ValueError("Reading date cannot be in the future.")

        previous_reading = (
            Reading.query.filter(
                Reading.meter_id == meter.id,
                Reading.reading_date < reading_date,
            )
            .order_by(Reading.reading_date.desc())
            .first()
        )
        next_reading = (
            Reading.query.filter(
                Reading.meter_id == meter.id,
                Reading.reading_date > reading_date,
            )
            .order_by(Reading.reading_date.asc())
            .first()
        )

        if previous_reading and value < previous_reading.reading_value:
            raise ValueError("Reading value cannot be lower than the previous reading.")
        if next_reading and value > next_reading.reading_value:
            raise ValueError("Reading value cannot be higher than the next reading.")

        reading = Reading(
            meter_id=meter.id,
            reading_date=reading_date,
            reading_value=value,
            reading_type=reading_type,
        )
        db.session.add(reading)
        db.session.commit()
        return reading
    except IntegrityError:
        db.session.rollback()
        raise ValueError("A reading already exists for this meter on that date.")
    except Exception:
        db.session.rollback()
        raise
