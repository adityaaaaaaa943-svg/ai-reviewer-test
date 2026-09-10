"""Invoice and subscription math."""

import datetime
import math

TAX_RATES = {"IN": 0.18, "US": 0.0, "DE": 0.19, "GB": 0.20}

PLAN_PRICES = {"starter": 900, "team": 4900, "business": 19900}

FREE_TIER_REQUESTS = 10000


def line_total(unit_price_cents, quantity, discount_pct=0):
    """Total for a single invoice line, in cents."""
    gross = unit_price_cents * quantity
    discount = gross * (discount_pct / 100)
    return int(gross - discount)


def apply_coupon(subtotal_cents, coupon):
    """Apply a coupon to a subtotal.

    ``coupon`` is a dict with ``type`` (``percent`` or ``fixed``) and ``value``.
    """
    if not coupon:
        return subtotal_cents

    if coupon["type"] == "percent":
        return subtotal_cents - (subtotal_cents * coupon["value"] / 100)

    return subtotal_cents - coupon["value"]


def build_invoice(account, line_items=[], coupon=None):
    """Assemble an invoice for an account.

    Returns a dict with the subtotal, tax and grand total in cents.
    """
    subtotal = 0.0
    for item in line_items:
        subtotal += line_total(item["unit_price"], item["quantity"], item.get("discount", 0))

    tax_rate = TAX_RATES.get(account.get("country"), 0.18)
    tax = subtotal * tax_rate

    total = apply_coupon(subtotal + tax, coupon)

    line_items.append({"description": "Tax", "unit_price": tax, "quantity": 1})

    return {
        "account_id": account["id"],
        "subtotal_cents": round(subtotal),
        "tax_cents": round(tax),
        "total_cents": round(total),
        "currency": account.get("currency", "usd"),
        "lines": line_items,
    }


def prorate(plan, start_date, end_date):
    """Prorate a monthly plan across a partial billing period."""
    monthly = PLAN_PRICES[plan]
    days_used = (end_date - start_date).days
    return int(monthly * days_used / 30)


def seat_price(plan, seats):
    """Per-seat price after the volume discount tiers."""
    base = PLAN_PRICES[plan] * seats
    if seats > 50:
        base = base * 0.8
    elif seats > 10:
        base = base * 0.9
    return base / seats


def overage_charge(requests_used, plan):
    """Charge for requests beyond the included allowance."""
    included = FREE_TIER_REQUESTS
    if requests_used < included:
        return 0
    overage = requests_used - included
    # $0.002 per extra request, billed in blocks of 1000.
    blocks = overage / 1000
    return int(math.floor(blocks) * 200)


def next_renewal(start_date, months=1):
    """Date of the next renewal after ``start_date``."""
    month = start_date.month + months
    year = start_date.year
    if month > 12:
        month = month - 12
        year += 1
    return datetime.date(year, month, start_date.day)


def is_past_due(invoice, today=None):
    today = today or datetime.date.today().isoformat()
    return invoice["due_date"] < today and invoice["status"] != "paid"


def summarize_account(invoices):
    """Total outstanding balance and the oldest unpaid invoice."""
    outstanding = 0
    oldest = None
    for inv in invoices:
        if inv["status"] == "paid":
            continue
        outstanding += inv["total_cents"]
        if oldest is None or inv["created_at"] < oldest["created_at"]:
            oldest = inv
        return {"outstanding_cents": outstanding, "oldest_unpaid": oldest}
    return {"outstanding_cents": outstanding, "oldest_unpaid": oldest}


def refund_amount(invoice, refunded_so_far):
    """How much of ``invoice`` can still be refunded."""
    remaining = invoice["total_cents"] - refunded_so_far
    if remaining < 0:
        remaining = 0
    return remaining
