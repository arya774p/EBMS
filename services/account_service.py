import random

from sqlalchemy.exc import IntegrityError

from extensions import bcrypt, db
from models import AppUser, Customer
from utils.forms import clean_text, validate_phone


def generate_account_no():
    while True:
        account_no = str(random.randint(1000000000, 9999999999))
        if not Customer.query.filter_by(account_no=account_no).first():
            return account_no


def create_customer_account(full_name, phone, email, password):
    full_name = clean_text(full_name)
    phone = validate_phone(phone)
    email = clean_text(email).lower()

    if not full_name:
        raise ValueError("Full name is required.")
    if not email:
        raise ValueError("Email is required.")
    if len(password or "") < 6:
        raise ValueError("Password must be at least 6 characters.")
    if AppUser.query.filter_by(email=email).first():
        raise ValueError("Email is already registered.")

    try:
        customer = Customer(
            account_no=generate_account_no(),
            full_name=full_name,
            phone=phone,
        )
        db.session.add(customer)
        db.session.flush()

        user = AppUser(
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            role="CUSTOMER",
            customer_id=customer.id,
        )
        db.session.add(user)
        db.session.commit()
        return user
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Could not create account because a unique value already exists.")
    except Exception:
        db.session.rollback()
        raise


def create_admin_user(email, password):
    email = clean_text(email).lower()
    if not email or len(password or "") < 6:
        raise ValueError("Admin email and a 6 character password are required.")
    if AppUser.query.filter_by(email=email).first():
        raise ValueError("Admin email already exists.")

    try:
        admin = AppUser(
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            role="ADMIN",
            customer_id=None,
        )
        db.session.add(admin)
        db.session.commit()
        return admin
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Admin email already exists.")
    except Exception:
        db.session.rollback()
        raise
