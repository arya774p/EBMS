from flask import render_template
from flask_login import login_required, current_user


def register_admin_routes(app):

    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        if current_user.role != "ADMIN":
            return "Access denied"

        return render_template("admin_dashboard.html")