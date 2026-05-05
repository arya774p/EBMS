from datetime import date

from sqlalchemy import func

from flask import flash, redirect, render_template, request, url_for

from extensions import db
from models import (
    Bill,
    Customer,
    Meter,
    MeterRequest,
    Payment,
    Reading,
    SQLQueryLog,
)
from services.bill_service import bill_net_amount, bill_summary_map, generate_bill_from_reading
from services.meter_service import approve_meter_request, reject_meter_request
from services.payment_service import PAYMENT_STATUSES, update_payment_status
from services.reading_service import add_meter_reading
from utils.auth import admin_required
from utils.forms import optional_text


def register_admin_routes(app):
    @app.route("/admin/dashboard")
    @admin_required
    def admin_dashboard():
        stats = {
            "customers": Customer.query.count(),
            "pending_requests": MeterRequest.query.filter_by(request_status="PENDING").count(),
            "active_meters": Meter.query.filter_by(status="ACTIVE").count(),
            "unpaid_bills": Bill.query.filter(Bill.status.in_(["GENERATED", "OVERDUE"])).count(),
            "payments_total": db.session.query(func.coalesce(func.sum(Payment.amount_paid), 0))
            .filter(Payment.status == "COMPLETED")
            .scalar(),
        }
        recent_requests = MeterRequest.query.order_by(MeterRequest.requested_at.desc()).limit(5).all()
        recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
        return render_template(
            "admin_dashboard.html",
            stats=stats,
            recent_requests=recent_requests,
            recent_payments=recent_payments,
        )

    @app.route("/admin/customers")
    @admin_required
    def admin_customers():
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        return render_template("admin/customers.html", customers=customers)

    @app.route("/admin/customers/<int:customer_id>")
    @admin_required
    def admin_customer_detail(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        bills = (
            Bill.query.join(Meter)
            .filter(Meter.customer_id == customer.id)
            .order_by(Bill.billing_end.desc())
            .all()
        )
        net_amounts = bill_summary_map([bill.id for bill in bills])
        return render_template(
            "admin/customer_detail.html",
            customer=customer,
            bills=bills,
            net_amounts=net_amounts,
        )

    @app.route("/admin/meter-requests")
    @admin_required
    def admin_meter_requests():
        status = optional_text(request.args.get("status"))
        query = MeterRequest.query
        if status:
            query = query.filter_by(request_status=status)
        requests = query.order_by(MeterRequest.requested_at.desc()).all()
        return render_template("admin/meter_requests.html", requests=requests, selected_status=status)

    @app.route("/admin/meter-requests/<int:request_id>")
    @admin_required
    def admin_meter_request_detail(request_id):
        meter_request = MeterRequest.query.get_or_404(request_id)
        return render_template("admin/meter_request_detail.html", meter_request=meter_request)

    @app.route("/admin/meter-requests/<int:request_id>/approve", methods=["POST"])
    @admin_required
    def admin_approve_meter_request(request_id):
        try:
            meter = approve_meter_request(request_id, request.form.get("admin_note"))
            flash(f"Request approved. Meter {meter.meter_no} created.", "success")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("admin_meter_request_detail", request_id=request_id))

    @app.route("/admin/meter-requests/<int:request_id>/reject", methods=["POST"])
    @admin_required
    def admin_reject_meter_request(request_id):
        try:
            reject_meter_request(request_id, request.form.get("admin_note"))
            flash("Request rejected.", "success")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("admin_meter_request_detail", request_id=request_id))

    @app.route("/admin/meters")
    @admin_required
    def admin_meters():
        meters = Meter.query.order_by(Meter.installation_date.desc(), Meter.id.desc()).all()
        return render_template("admin/meters.html", meters=meters)

    @app.route("/admin/meters/<int:meter_id>")
    @admin_required
    def admin_meter_detail(meter_id):
        meter = Meter.query.get_or_404(meter_id)
        bills = Bill.query.filter_by(meter_id=meter.id).order_by(Bill.billing_end.desc()).all()
        net_amounts = bill_summary_map([bill.id for bill in bills])
        return render_template("admin/meter_detail.html", meter=meter, bills=bills, net_amounts=net_amounts)

    @app.route("/admin/meters/<int:meter_id>/status", methods=["POST"])
    @admin_required
    def admin_update_meter_status(meter_id):
        meter = Meter.query.get_or_404(meter_id)
        status = request.form.get("status")
        if status not in {"ACTIVE", "DISCONNECTED", "FAULTY", "INACTIVE"}:
            flash("Invalid meter status.", "error")
            return redirect(url_for("admin_meter_detail", meter_id=meter.id))

        meter.status = status
        meter.disconnection_date = date.today() if status == "DISCONNECTED" else None
        db.session.commit()
        flash("Meter status updated.", "success")
        return redirect(url_for("admin_meter_detail", meter_id=meter.id))

    @app.route("/admin/readings")
    @admin_required
    def admin_readings():
        readings = Reading.query.join(Meter).order_by(Reading.reading_date.desc(), Reading.id.desc()).all()
        return render_template("admin/readings.html", readings=readings)

    @app.route("/admin/readings/new", methods=["GET", "POST"])
    @admin_required
    def admin_new_reading():
        meters = Meter.query.order_by(Meter.meter_no.asc()).all()
        if request.method == "POST":
            try:
                reading = add_meter_reading(
                    int(request.form.get("meter_id")),
                    request.form.get("reading_date"),
                    request.form.get("reading_value"),
                    request.form.get("reading_type"),
                )
                flash("Reading added.", "success")
                return redirect(url_for("admin_meter_detail", meter_id=reading.meter_id))
            except (TypeError, ValueError) as error:
                flash(str(error), "error")
        return render_template("admin/reading_form.html", meters=meters)

    @app.route("/admin/bills")
    @admin_required
    def admin_bills():
        bills = Bill.query.order_by(Bill.bill_generated_at.desc()).all()
        net_amounts = bill_summary_map([bill.id for bill in bills])
        return render_template("admin/bills.html", bills=bills, net_amounts=net_amounts)

    @app.route("/admin/bills/<int:bill_id>")
    @admin_required
    def admin_bill_detail(bill_id):
        bill = Bill.query.get_or_404(bill_id)
        return render_template("admin/bill_detail.html", bill=bill, net_amount=bill_net_amount(bill.id))

    @app.route("/admin/bills/generate", methods=["GET", "POST"])
    @admin_required
    def admin_generate_bill():
        if request.method == "POST":
            try:
                bill = generate_bill_from_reading(int(request.form.get("current_reading_id")))
                flash("Bill generated.", "success")
                return redirect(url_for("admin_bill_detail", bill_id=bill.id))
            except (TypeError, ValueError) as error:
                flash(str(error), "error")

        billed_reading_ids = db.session.query(Bill.current_reading_id)
        readings = (
            Reading.query.join(Meter)
            .filter(~Reading.id.in_(billed_reading_ids))
            .order_by(Meter.meter_no.asc(), Reading.reading_date.desc())
            .all()
        )
        return render_template("admin/bill_generate.html", readings=readings)

    @app.route("/admin/bills/<int:bill_id>/status", methods=["POST"])
    @admin_required
    def admin_update_bill_status(bill_id):
        bill = Bill.query.get_or_404(bill_id)
        status = request.form.get("status")
        if status not in {"GENERATED", "PAID", "OVERDUE", "CANCELLED"}:
            flash("Invalid bill status.", "error")
            return redirect(url_for("admin_bill_detail", bill_id=bill.id))

        bill.status = status
        db.session.commit()
        flash("Bill status updated.", "success")
        return redirect(url_for("admin_bill_detail", bill_id=bill.id))

    @app.route("/admin/payments")
    @admin_required
    def admin_payments():
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        return render_template("admin/payments.html", payments=payments, statuses=sorted(PAYMENT_STATUSES))

    @app.route("/admin/payments/<int:payment_id>/status", methods=["POST"])
    @admin_required
    def admin_update_payment_status(payment_id):
        try:
            update_payment_status(payment_id, request.form.get("status"))
            flash("Payment status updated.", "success")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("admin_payments"))

    @app.route("/admin/sql-queries")
    @admin_required
    def admin_sql_queries():
        query = SQLQueryLog.query
        statement = optional_text(request.args.get("statement_type"))
        route_path = optional_text(request.args.get("route_path"))
        user_role = optional_text(request.args.get("user_role"))
        success = optional_text(request.args.get("success"))

        if statement:
            query = query.filter(SQLQueryLog.statement_type == statement.upper())
        if route_path:
            query = query.filter(SQLQueryLog.route_path.like(f"%{route_path}%"))
        if user_role:
            query = query.filter(SQLQueryLog.user_role == user_role.upper())
        if success in {"0", "1"}:
            query = query.filter(SQLQueryLog.success == (success == "1"))

        logs = query.order_by(SQLQueryLog.executed_at.desc()).limit(200).all()
        statement_types = [
            item[0]
            for item in db.session.query(SQLQueryLog.statement_type)
            .distinct()
            .order_by(SQLQueryLog.statement_type.asc())
            .all()
            if item[0]
        ]
        return render_template(
            "admin/sql_queries.html",
            logs=logs,
            statement_types=statement_types,
            filters={
                "statement_type": statement,
                "route_path": route_path,
                "user_role": user_role,
                "success": success,
            },
        )

    @app.route("/admin/sql-queries/<int:log_id>")
    @admin_required
    def admin_sql_query_detail(log_id):
        log = SQLQueryLog.query.get_or_404(log_id)
        return render_template("admin/sql_query_detail.html", log=log)
