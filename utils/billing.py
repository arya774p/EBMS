from decimal import Decimal


DOMESTIC_SLABS = (
    (Decimal("100"), Decimal("4.00")),
    (Decimal("100"), Decimal("6.00")),
    (None, Decimal("8.00")),
)

COMMERCIAL_SLABS = (
    (Decimal("100"), Decimal("8.00")),
    (Decimal("100"), Decimal("10.00")),
    (None, Decimal("12.00")),
)


def calculate_bill_amount(category, units):
    units_left = Decimal(units)
    total = Decimal("0.00")
    slabs = DOMESTIC_SLABS if category == "DOMESTIC" else COMMERCIAL_SLABS

    for slab_units, rate in slabs:
        if units_left <= 0:
            break

        billable_units = units_left if slab_units is None else min(units_left, slab_units)
        total += billable_units * rate
        units_left -= billable_units

    return total.quantize(Decimal("0.01"))
