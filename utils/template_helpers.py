from decimal import Decimal, InvalidOperation


def format_money(value):
    if value is None:
        return "Rs. 0.00"
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        return f"Rs. {value}"
    return f"Rs. {amount:,.2f}"


def status_class(status):
    status = (status or "").upper()
    if status in {"APPROVED", "ACTIVE", "PAID", "COMPLETED", "ACTUAL"}:
        return "bg-emerald-100 text-emerald-700 ring-emerald-200"
    if status in {"PENDING", "GENERATED", "ESTIMATED"}:
        return "bg-amber-100 text-amber-800 ring-amber-200"
    if status in {"REJECTED", "FAILED", "OVERDUE", "DISCONNECTED", "FAULTY"}:
        return "bg-rose-100 text-rose-700 ring-rose-200"
    if status in {"CANCELLED", "REFUNDED", "INACTIVE"}:
        return "bg-slate-100 text-slate-700 ring-slate-200"
    return "bg-slate-100 text-slate-700 ring-slate-200"


def register_template_helpers(app):
    app.add_template_filter(format_money, "money")

    @app.context_processor
    def inject_helpers():
        return {"status_class": status_class}
