from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from extensions import bcrypt
from models import AppUser
from services.account_service import create_customer_account
from utils.auth import role_home
from utils.forms import clean_text


def register_auth_routes(app):
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for(role_home()))

        if request.method == "POST":
            try:
                create_customer_account(
                    request.form.get("full_name"),
                    request.form.get("phone"),
                    request.form.get("email"),
                    request.form.get("password"),
                )
                flash("Account created successfully. Please login.", "success")
                return redirect(url_for("login"))
            except ValueError as error:
                flash(str(error), "error")

        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for(role_home()))

        if request.method == "POST":
            email = clean_text(request.form.get("email")).lower()
            password = request.form.get("password")
            user = AppUser.query.filter_by(email=email).first()

            if user and user.is_active and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(url_for(role_home()))

            flash("Invalid email or password.", "error")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))
