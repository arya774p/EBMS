from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user, login_required


def role_home():
    if current_user.is_authenticated and current_user.role == "ADMIN":
        return "admin_dashboard"
    if current_user.is_authenticated and current_user.role == "CUSTOMER":
        return "customer_dashboard"
    return "login"


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "ADMIN":
            flash("You do not have permission to open that page.", "error")
            return redirect(url_for(role_home()))
        return view_func(*args, **kwargs)

    return wrapped


def customer_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "CUSTOMER":
            flash("You do not have permission to open that page.", "error")
            return redirect(url_for(role_home()))
        if not current_user.customer:
            flash("Your customer profile is missing. Contact the administrator.", "error")
            return redirect(url_for("logout"))
        return view_func(*args, **kwargs)

    return wrapped
