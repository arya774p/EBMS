from sqlalchemy.exc import IntegrityError

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from extensions import db
from models import Address, Bill, Meter, MeterRequest, Payment
from services.bill_service import bill_net_amount, bill_summary_map
from services.payment_service import PAYMENT_METHODS, pay_customer_bill
from utils.auth import customer_required
from utils.forms import (
    clean_text,
    optional_text,
    parse_decimal,
    validate_phone,
    validate_pincode,
)


def register_customer_routes(app):
    @app.route("/customer/dashboard")
    @customer_required
    def customer_dashboard():
        customer_id = current_user.customer_id
        bills = (
            Bill.query.join(Meter)
            .filter(Meter.customer_id == customer_id)
            .order_by(Bill.bill_generated_at.desc())
            .limit(5)
            .all()
        )
        net_amounts = bill_summary_map([bill.id for bill in bills])
        stats = {
            "addresses": Address.query.filter_by(customer_id=customer_id).count(),
            "meter_requests": MeterRequest.query.filter_by(customer_id=customer_id).count(),
            "active_meters": Meter.query.filter_by(customer_id=customer_id, status="ACTIVE").count(),
            "unpaid_bills": (
                Bill.query.join(Meter)
                .filter(Meter.customer_id == customer_id, Bill.status.in_(["GENERATED", "OVERDUE"]))
                .count()
            ),
        }
        return render_template("customer_dashboard.html", stats=stats, bills=bills, net_amounts=net_amounts)

    @app.route("/customer/profile", methods=["GET", "POST"])
    @customer_required
    def customer_profile():
        customer = current_user.customer
        if request.method == "POST":
            try:
                full_name = clean_text(request.form.get("full_name"))
                if not full_name:
                    raise ValueError("Full name is required.")
                customer.full_name = full_name
                customer.phone = validate_phone(request.form.get("phone"))
                db.session.commit()
                flash("Profile updated.", "success")
                return redirect(url_for("customer_profile"))
            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")

        return render_template("customer/profile.html", customer=customer)

    @app.route("/customer/addresses", methods=["GET", "POST"])
    @customer_required
    def customer_addresses():
        customer_id = current_user.customer_id
        if request.method == "POST":
            try:
                address = build_address_from_form(customer_id)
                db.session.add(address)
                db.session.commit()
                flash("Address added.", "success")
                return redirect(url_for("customer_addresses"))
            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")

        addresses = Address.query.filter_by(customer_id=customer_id).order_by(Address.created_at.desc()).all()
        return render_template("customer/addresses.html", addresses=addresses)

    @app.route("/customer/addresses/<int:address_id>/edit", methods=["GET", "POST"])
    @customer_required
    def edit_customer_address(address_id):
        address = customer_address_or_404(address_id)
        if request.method == "POST":
            try:
                update_address_from_form(address)
                db.session.commit()
                flash("Address updated.", "success")
                return redirect(url_for("customer_addresses"))
            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")

        return render_template("customer/address_form.html", address=address)

    @app.route("/customer/addresses/<int:address_id>/delete", methods=["POST"])
    @customer_required
    def delete_customer_address(address_id):
        address = customer_address_or_404(address_id)
        try:
            db.session.delete(address)
            db.session.commit()
            flash("Address deleted.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("This address is linked to a meter or request and cannot be deleted.", "error")
        return redirect(url_for("customer_addresses"))

    @app.route("/customer/meter-requests")
    @customer_required
    def customer_meter_requests():
        requests = (
            MeterRequest.query.filter_by(customer_id=current_user.customer_id)
            .order_by(MeterRequest.requested_at.desc())
            .all()
        )
        return render_template("customer/meter_requests.html", requests=requests)

    @app.route("/customer/meter-requests/new", methods=["GET", "POST"])
    @customer_required
    def new_meter_request():
        addresses = Address.query.filter_by(customer_id=current_user.customer_id).order_by(Address.created_at.desc()).all()
        if request.method == "POST":
            try:
                if not addresses:
                    raise ValueError("Add an address before requesting a meter.")

                address_id = int(request.form.get("address_id"))
                address = Address.query.filter_by(id=address_id, customer_id=current_user.customer_id).first()
                if not address:
                    raise ValueError("Choose one of your saved addresses.")

                category = request.form.get("category")
                if category not in {"DOMESTIC", "COMMERCIAL"}:
                    raise ValueError("Invalid meter category.")

                meter_request = MeterRequest(
                    customer_id=current_user.customer_id,
                    address_id=address.id,
                    category=category,
                    sanction_load=parse_decimal(request.form.get("sanction_load"), "Sanction load", minimum=0.01),
                    max_demand=parse_optional_decimal(request.form.get("max_demand"), "Max demand"),
                    request_status="PENDING",
                )
                db.session.add(meter_request)
                db.session.commit()
                flash("Meter request submitted.", "success")
                return redirect(url_for("customer_meter_requests"))
            except (TypeError, ValueError) as error:
                db.session.rollback()
                flash(str(error), "error")

        return render_template("customer/meter_request_form.html", addresses=addresses)

    @app.route("/customer/meter-requests/<int:request_id>/cancel", methods=["POST"])
    @customer_required
    def cancel_meter_request(request_id):
        meter_request = (
            MeterRequest.query.filter_by(id=request_id, customer_id=current_user.customer_id)
            .with_for_update()
            .first()
        )
        if not meter_request:
            abort(404)
        if meter_request.request_status != "PENDING":
            flash("Only pending requests can be cancelled.", "error")
            return redirect(url_for("customer_meter_requests"))

        meter_request.request_status = "CANCELLED"
        db.session.commit()
        flash("Meter request cancelled.", "success")
        return redirect(url_for("customer_meter_requests"))

    @app.route("/customer/meters")
    @customer_required
    def customer_meters():
        meters = Meter.query.filter_by(customer_id=current_user.customer_id).order_by(Meter.installation_date.desc()).all()
        return render_template("customer/meters.html", meters=meters)

    @app.route("/customer/meters/<int:meter_id>")
    @customer_required
    def customer_meter_detail(meter_id):
        meter = customer_meter_or_404(meter_id)
        bills = Bill.query.filter_by(meter_id=meter.id).order_by(Bill.billing_end.desc()).all()
        net_amounts = bill_summary_map([bill.id for bill in bills])
        return render_template("customer/meter_detail.html", meter=meter, bills=bills, net_amounts=net_amounts)

    @app.route("/customer/bills")
    @customer_required
    def customer_bills():
        bills = (
            Bill.query.join(Meter)
            .filter(Meter.customer_id == current_user.customer_id)
            .order_by(Bill.billing_end.desc())
            .all()
        )
        net_amounts = bill_summary_map([bill.id for bill in bills])
        return render_template("customer/bills.html", bills=bills, net_amounts=net_amounts)

    @app.route("/customer/bills/<int:bill_id>")
    @customer_required
    def customer_bill_detail(bill_id):
        bill = customer_bill_or_404(bill_id)
        return render_template(
            "customer/bill_detail.html",
            bill=bill,
            net_amount=bill_net_amount(bill.id),
            payment_methods=sorted(PAYMENT_METHODS),
        )

    @app.route("/customer/bills/<int:bill_id>/pay", methods=["POST"])
    @customer_required
    def pay_bill(bill_id):
        try:
            pay_customer_bill(
                bill_id,
                current_user.customer_id,
                request.form.get("payment_method"),
                optional_text(request.form.get("transaction_ref")),
            )
            flash("Payment completed and bill marked as paid.", "success")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("customer_bill_detail", bill_id=bill_id))

    @app.route("/customer/payments")
    @customer_required
    def customer_payments():
        payments = (
            Payment.query.join(Bill)
            .join(Meter)
            .filter(Meter.customer_id == current_user.customer_id)
            .order_by(Payment.payment_date.desc())
            .all()
        )
        return render_template("customer/payments.html", payments=payments)


def customer_address_or_404(address_id):
    address = Address.query.filter_by(id=address_id, customer_id=current_user.customer_id).first()
    if not address:
        abort(404)
    return address


def customer_meter_or_404(meter_id):
    meter = Meter.query.filter_by(id=meter_id, customer_id=current_user.customer_id).first()
    if not meter:
        abort(404)
    return meter


def customer_bill_or_404(bill_id):
    bill = Bill.query.join(Meter).filter(Bill.id == bill_id, Meter.customer_id == current_user.customer_id).first()
    if not bill:
        abort(404)
    return bill


def build_address_from_form(customer_id):
    address = Address(customer_id=customer_id)
    update_address_from_form(address)
    return address


def update_address_from_form(address):
    address.base_address = clean_text(request.form.get("base_address"))
    address.locality = optional_text(request.form.get("locality"))
    address.city = clean_text(request.form.get("city"))
    address.state = clean_text(request.form.get("state"))
    address.pincode = validate_pincode(request.form.get("pincode"))

    if not address.base_address:
        raise ValueError("Base address is required.")
    if not address.city:
        raise ValueError("City is required.")
    if not address.state:
        raise ValueError("State is required.")


def parse_optional_decimal(value, field_name):
    if not optional_text(value):
        return None
    return parse_decimal(value, field_name, minimum=0)
