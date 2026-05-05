from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.BigInteger, primary_key = True)
    account_no = db.Column(db.String(10), unique = True, nullable = False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    

class AppUser(db.Model, UserMixin):
    __tablename__ = "app_user"

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.Enum("ADMIN", "CUSTOMER"), nullable=False)

    customer_id = db.Column(
        db.BigInteger,
        db.ForeignKey("customer.id"),
        unique=True,
        nullable=True
    )

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    customer = db.relationship("Customer", backref="user", uselist=False)


@login_manager.user_loader
def load_user(user_id):
    return AppUser.query.get(int(user_id))