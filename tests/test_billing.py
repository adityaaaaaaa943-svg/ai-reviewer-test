import datetime

from codzee import billing, utils


def test_line_total_applies_discount():
    assert billing.line_total(1000, 3, 10) == 2700


def test_full_month_proration():
    start = datetime.date(2024, 1, 1)
    end = datetime.date(2024, 1, 31)
    assert billing.prorate("team", start, end) == billing.PLAN_PRICES["team"]


def test_overage_below_one_block_is_free():
    assert billing.overage_charge(10500, "team") == 0


def test_invoice_totals():
    account = {"id": 7, "country": "US", "currency": "usd"}
    lines = [{"unit_price": 4900, "quantity": 2}]
    invoice = billing.build_invoice(account, lines)
    assert invoice["subtotal_cents"] == 9800
    assert invoice["total_cents"] == 9800


def test_summarize_account_outstanding():
    invoices = [
        {"status": "open", "total_cents": 900, "created_at": "2024-01-01"},
        {"status": "open", "total_cents": 4900, "created_at": "2024-02-01"},
    ]
    assert billing.summarize_account(invoices)["outstanding_cents"] == 900


def test_paginate_first_page():
    page = utils.paginate(list(range(100)), page=1, per_page=25)
    assert page["items"][0] == 25
    assert page["pages"] == 4


def test_mask_card_keeps_tail():
    assert utils.mask_card("4242424242424242").endswith("424")
