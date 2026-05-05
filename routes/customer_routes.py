from flask import render_template
from flask_login import login_required, current_user


def register_customer_routes(app):

    @app.route("/customer/dashboard")
    @login_required
    def customer_dashboard():
        if current_user.role != "CUSTOMER":
            return "Access denied"

        return render_template("customer_dashboard.html")