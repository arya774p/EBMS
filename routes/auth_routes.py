from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from extensions import db, bcrypt
from models import Customer, AppUser
import random

def generate_account_no():
    while True:
        account_no = str(random.randint(1000000000, 9999999999))
        existing = Customer.query.filter_by(account_no=account_no).first()
        if not existing:
            return account_no
        
def register_auth_routes(app):
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            full_name = request.form["full_name"]
            phone = request.form["phone"]
            email = request.form["email"]
            password = request.form["password"]

            existing_user = AppUser.query.filter_by(email=email).first()
            if existing_user:
                return "Email already registered"

            customer = Customer(
                account_no=generate_account_no(),
                full_name=full_name,
                phone=phone
            )

            db.session.add(customer)
            db.session.flush()

            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

            user = AppUser(
                email=email,
                password_hash=password_hash,
                role="CUSTOMER",
                customer_id=customer.id
            )

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("login"))

        return render_template("signup.html")
    
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            user = AppUser.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user)

                if user.role == "ADMIN":
                    return redirect(url_for("admin_dashboard"))

                return redirect(url_for("customer_dashboard"))

            return "Invalid email or password"

        return render_template("login.html")


    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))
    
    @app.route("/create-admin")
    def create_admin():
        email = "admin@gmail.com"
        password = "Admin123"

        existing = AppUser.query.filter_by(email=email).first()
        if existing:
            return "Admin already exists"

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        admin = AppUser(
            email=email,
            password_hash=password_hash,
            role="ADMIN",
            customer_id=None
        )

        db.session.add(admin)
        db.session.commit()

        return "Admin created successfully"