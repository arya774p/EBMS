from extensions import db
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