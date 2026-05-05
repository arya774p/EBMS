from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import myapp
from extensions import bcrypt, db
from models import (
    Address,
    AppUser,
    Bill,
    Customer,
    Meter,
    MeterRequest,
    Payment,
    Reading,
)
from utils.billing import calculate_bill_amount


CUSTOMER_NAMES = [
    "Soman Agarwal",
    "Riya Yadav",
    "Vansh Kumar",
    "Gitanjali Sharma",
    "Anurag Thakur",
    "Gopal Krishna",
    "Om Sarraf",
    "Hardik Sharma",
    "Kiran Joshi",
    "Kavya Singh",
]

PAYMENT_METHODS = ["UPI", "DEBIT_CARD", "CREDIT_CARD", "CASH"]
START_DATE = date(2026, 3, 1)
END_DATE = date(2026, 8, 31)


def account_no(index):
    return f"76{index:08d}"


def email_for(name):
    first, last = name.lower().split()[0], name.lower().split()[-1]
    return f"{first}.{last}@gmail.com"


def phone_for(index):
    return f"98765{index:05d}"


def meter_no(customer_index, meter_index):
    return f"EBMS{customer_index:02d}{meter_index:03d}"


def reset_existing_demo_data():
    emails = [email_for(name) for name in CUSTOMER_NAMES]
    users = AppUser.query.filter(AppUser.email.in_(emails)).all()
    customer_ids = [user.customer_id for user in users if user.customer_id]

    if not customer_ids:
        return

    meter_ids = [meter.id for meter in Meter.query.filter(Meter.customer_id.in_(customer_ids)).all()]
    bill_ids = [bill.id for bill in Bill.query.filter(Bill.meter_id.in_(meter_ids)).all()] if meter_ids else []

    if bill_ids:
        Payment.query.filter(Payment.bill_id.in_(bill_ids)).delete(synchronize_session=False)
        Bill.query.filter(Bill.id.in_(bill_ids)).delete(synchronize_session=False)
    if meter_ids:
        Reading.query.filter(Reading.meter_id.in_(meter_ids)).delete(synchronize_session=False)
        Meter.query.filter(Meter.id.in_(meter_ids)).delete(synchronize_session=False)

    MeterRequest.query.filter(MeterRequest.customer_id.in_(customer_ids)).delete(synchronize_session=False)
    Address.query.filter(Address.customer_id.in_(customer_ids)).delete(synchronize_session=False)
    AppUser.query.filter(AppUser.email.in_(emails)).delete(synchronize_session=False)
    Customer.query.filter(Customer.id.in_(customer_ids)).delete(synchronize_session=False)
    db.session.commit()


def category_plan(customer_index, meter_count):
    if customer_index % 3 == 1:
        return ["DOMESTIC"] * meter_count
    if customer_index % 3 == 2:
        return ["COMMERCIAL"] * meter_count
    return [random.choice(["DOMESTIC", "COMMERCIAL"]) for _ in range(meter_count)]


def create_customer(index, name):
    customer = Customer(
        account_no=account_no(index),
        full_name=name,
        phone=phone_for(index),
    )
    db.session.add(customer)
    db.session.flush()

    user = AppUser(
        email=email_for(name),
        password_hash=bcrypt.generate_password_hash("Admin123").decode("utf-8"),
        role="CUSTOMER",
        customer_id=customer.id,
        is_active=True,
    )
    db.session.add(user)
    return customer


def create_addresses(customer, index):
    cities = [
        ("Bareilly", "Uttar Pradesh", "243001"),
        ("Lucknow", "Uttar Pradesh", "226001"),
        ("Delhi", "Delhi", "110001"),
        ("Jaipur", "Rajasthan", "302001"),
        ("Noida", "Uttar Pradesh", "201301"),
    ]
    city, state, pincode = cities[index % len(cities)]
    address_count = 2 if index % 4 == 0 else 1
    addresses = []

    for address_index in range(1, address_count + 1):
        address = Address(
            customer_id=customer.id,
            base_address=f"House No. {20 + index}-{address_index}, Sector {address_index + index}",
            locality=random.choice(["Civil Lines", "Green Park", "Main Market", "Station Road", "Shastri Nagar"]),
            city=city,
            state=state,
            pincode=pincode,
        )
        db.session.add(address)
        addresses.append(address)

    db.session.flush()
    return addresses


def create_meter_request_and_meter(customer, address, customer_index, meter_index, category):
    sanction_load = Decimal(random.choice(["1.50", "2.00", "3.00", "5.00", "7.50"]))
    max_demand = None
    if category == "COMMERCIAL":
        max_demand = Decimal(random.choice(["4.00", "6.00", "8.50", "10.00"]))

    requested_at = random_datetime(date(2026, 3, 1), date(2026, 4, 15))
    reviewed_at = requested_at + timedelta(days=random.randint(1, 7))

    request = MeterRequest(
        customer_id=customer.id,
        address_id=address.id,
        category=category,
        sanction_load=sanction_load,
        max_demand=max_demand,
        request_status="APPROVED",
        requested_at=requested_at,
        reviewed_at=reviewed_at,
        admin_note="Approved after document verification.",
    )
    db.session.add(request)
    db.session.flush()

    meter = Meter(
        customer_id=customer.id,
        address_id=address.id,
        meter_request_id=request.id,
        meter_no=meter_no(customer_index, meter_index),
        category=category,
        sanction_load=sanction_load,
        max_demand=max_demand,
        status=random.choices(
            ["ACTIVE", "ACTIVE", "ACTIVE", "FAULTY", "INACTIVE"],
            weights=[70, 10, 10, 5, 5],
        )[0],
        installation_date=requested_at.date() + timedelta(days=random.randint(3, 12)),
    )
    db.session.add(meter)
    db.session.flush()
    return meter


def create_readings(meter):
    reading_count = random.randint(5, 8)
    first_date = max(START_DATE, meter.installation_date)
    if first_date > END_DATE:
        first_date = START_DATE

    available_days = (END_DATE - first_date).days
    step = max(14, available_days // reading_count)
    current_date = first_date + timedelta(days=random.randint(0, 4))
    current_value = Decimal(random.randint(80, 250))
    readings = []

    for reading_index in range(reading_count):
        if current_date > END_DATE:
            break

        reading = Reading(
            meter_id=meter.id,
            reading_date=current_date,
            reading_value=current_value.quantize(Decimal("0.01")),
            reading_type=random.choices(["ACTUAL", "ESTIMATED"], weights=[85, 15])[0],
        )
        db.session.add(reading)
        readings.append(reading)

        units_increment = random.randint(45, 180)
        if meter.category == "COMMERCIAL":
            units_increment += random.randint(80, 240)
        current_value += Decimal(units_increment)
        current_date += timedelta(days=step + random.randint(0, 8))

    db.session.flush()
    return readings


def create_bills_and_payments(meter, readings):
    sorted_readings = sorted(readings, key=lambda item: item.reading_date)

    for index in range(1, len(sorted_readings)):
        if random.random() > 0.82:
            continue

        previous_reading = sorted_readings[index - 1]
        current_reading = sorted_readings[index]
        units = current_reading.reading_value - previous_reading.reading_value
        gross_amount = calculate_bill_amount(meter.category, units)

        status = random.choices(
            ["GENERATED", "PAID", "OVERDUE", "CANCELLED"],
            weights=[20, 55, 15, 10],
        )[0]
        bill = Bill(
            meter_id=meter.id,
            previous_reading_id=previous_reading.id,
            current_reading_id=current_reading.id,
            bill_generated_at=datetime.combine(current_reading.reading_date, datetime.min.time()) + timedelta(hours=10),
            billing_start=previous_reading.reading_date,
            billing_end=current_reading.reading_date,
            due_date=current_reading.reading_date + timedelta(days=15),
            units_consumed=units.quantize(Decimal("0.01")),
            gross_amount=gross_amount,
            late_payment_surcharge=Decimal("0.00") if status != "OVERDUE" else Decimal(random.choice(["25.00", "50.00", "75.00"])),
            subsidy=Decimal(random.choice(["0.00", "50.00", "100.00"])) if meter.category == "DOMESTIC" else Decimal("0.00"),
            advance_adjusted=Decimal(random.choice(["0.00", "25.00", "40.00"])),
            status=status,
        )
        db.session.add(bill)
        db.session.flush()

        if status == "PAID":
            net_amount = bill.net_amount
            payment = Payment(
                bill_id=bill.id,
                payment_date=datetime.combine(
                    min(bill.due_date - timedelta(days=random.randint(0, 7)), END_DATE),
                    datetime.min.time(),
                ) + timedelta(hours=random.randint(9, 20), minutes=random.randint(0, 59)),
                amount_paid=net_amount,
                status="COMPLETED",
                payment_method=random.choice(PAYMENT_METHODS),
                transaction_ref=f"TXN{bill.id:05d}{random.randint(1000, 9999)}",
            )
            db.session.add(payment)
        elif status == "OVERDUE" and random.random() < 0.25:
            payment = Payment(
                bill_id=bill.id,
                payment_date=datetime.combine(min(bill.due_date + timedelta(days=3), END_DATE), datetime.min.time()),
                amount_paid=bill.net_amount,
                status=random.choice(["PENDING", "FAILED"]),
                payment_method=random.choice(PAYMENT_METHODS),
                transaction_ref=f"TXNFAIL{bill.id:05d}",
            )
            db.session.add(payment)


def random_datetime(start, end):
    days = (end - start).days
    selected = start + timedelta(days=random.randint(0, max(days, 0)))
    return datetime.combine(selected, datetime.min.time()) + timedelta(
        hours=random.randint(9, 17),
        minutes=random.randint(0, 59),
    )


def seed_demo_data():
    random.seed(20260505)
    reset_existing_demo_data()

    total_meters = 0
    total_readings = 0
    total_bills = 0

    for customer_index, name in enumerate(CUSTOMER_NAMES, start=1):
        customer = create_customer(customer_index, name)
        addresses = create_addresses(customer, customer_index)
        meter_count = random.randint(1, 5)
        categories = category_plan(customer_index, meter_count)

        for meter_index, category in enumerate(categories, start=1):
            address = random.choice(addresses)
            meter = create_meter_request_and_meter(
                customer,
                address,
                customer_index,
                meter_index,
                category,
            )
            readings = create_readings(meter)
            create_bills_and_payments(meter, readings)

            total_meters += 1
            total_readings += len(readings)

    db.session.flush()
    total_bills = Bill.query.count()
    db.session.commit()

    print("Demo data created successfully.")
    print(f"Customers: {len(CUSTOMER_NAMES)}")
    print(f"Meters: {total_meters}")
    print(f"Readings: {total_readings}")
    print(f"Total bills in database: {total_bills}")


if __name__ == "__main__":
    with myapp.app_context():
        seed_demo_data()
