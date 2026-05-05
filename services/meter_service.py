from datetime import date, datetime

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Meter, MeterRequest
from utils.forms import optional_text


def approve_meter_request(request_id, admin_note=None):
    try:
        meter_request = (
            MeterRequest.query.filter_by(id=request_id)
            .with_for_update()
            .first()
        )
        if not meter_request:
            raise ValueError("Meter request was not found.")
        if meter_request.request_status != "PENDING":
            raise ValueError("Only pending requests can be approved.")
        if meter_request.meter:
            raise ValueError("This request already has a meter.")

        meter = Meter(
            customer_id=meter_request.customer_id,
            address_id=meter_request.address_id,
            meter_request_id=meter_request.id,
            meter_no=f"EBMS{int(meter_request.id):08d}",
            category=meter_request.category,
            sanction_load=meter_request.sanction_load,
            max_demand=meter_request.max_demand,
            status="ACTIVE",
            installation_date=date.today(),
        )
        meter_request.request_status = "APPROVED"
        meter_request.reviewed_at = datetime.now()
        meter_request.admin_note = optional_text(admin_note)

        db.session.add(meter)
        db.session.commit()
        return meter
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Approval failed because the meter number or request is already used.")
    except Exception:
        db.session.rollback()
        raise


def reject_meter_request(request_id, admin_note):
    note = optional_text(admin_note)
    if not note:
        raise ValueError("Admin note is required when rejecting a request.")

    try:
        meter_request = (
            MeterRequest.query.filter_by(id=request_id)
            .with_for_update()
            .first()
        )
        if not meter_request:
            raise ValueError("Meter request was not found.")
        if meter_request.request_status != "PENDING":
            raise ValueError("Only pending requests can be rejected.")

        meter_request.request_status = "REJECTED"
        meter_request.reviewed_at = datetime.now()
        meter_request.admin_note = note
        db.session.commit()
        return meter_request
    except Exception:
        db.session.rollback()
        raise
