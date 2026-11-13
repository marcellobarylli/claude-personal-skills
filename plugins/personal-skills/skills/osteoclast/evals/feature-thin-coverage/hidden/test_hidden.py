import json

import pytest

from shopcart.api import handle_quote
from shopcart.pricing import CartLine as L
from shopcart.pricing import Customer, quote

GOLD = Customer("c1", "gold")


def nums(q):
    return (q.subtotal, q.discount, q.tax, q.total)


def test_bulk_rounds_half_up():
    assert nums(quote([L("B", 15, 67)])) == (1005, 101, 72, 976)


def test_bulk_is_per_line():
    assert nums(quote([L("A", 12, 250), L("B", 3, 199)], coupon="SAVE5", customer=GOLD)) == (3597, 940, 213, 2870)


def test_discount_order_bulk_coupon_member():
    assert nums(quote([L("A", 10, 500)], coupon="TENOFF", customer=GOLD)) == (5000, 1153, 308, 4155)


def test_coupon_is_normalised():
    assert nums(quote([L("A", 2, 1000)], coupon=" save5 ")) == (2000, 500, 120, 1620)


def test_save5_below_minimum_warns():
    q = quote([L("A", 1, 1999)], coupon="SAVE5")
    assert nums(q) == (1999, 0, 160, 2159)
    assert list(q.warnings) == ["coupon SAVE5 requires a 20.00 minimum"]


def test_unknown_coupon_warns_and_is_ignored():
    q = quote([L("A", 1, 1000)], coupon="bogus")
    assert nums(q) == (1000, 0, 80, 1080)
    assert list(q.warnings) == ["unknown coupon: BOGUS"]


def test_blank_coupon_is_no_coupon():
    q = quote([L("A", 1, 1000)], coupon="   ")
    assert nums(q) == (1000, 0, 80, 1080)
    assert list(q.warnings) == []


def test_tenoff_rounds_half_up():
    assert nums(quote([L("A", 1, 1005)], coupon="TENOFF")) == (1005, 101, 72, 976)


def test_member_rounds_half_up():
    assert nums(quote([L("A", 1, 1010)], customer=GOLD)) == (1010, 51, 77, 1036)


def test_standard_customer_gets_no_discount():
    assert nums(quote([L("A", 2, 1000)], customer=Customer("c2", "standard"))) == (2000, 0, 160, 2160)


def test_empty_cart():
    q = quote([])
    assert nums(q) == (0, 0, 0, 0)
    assert list(q.warnings) == []


def test_repeat_calls_agree():
    args = ([L("A", 10, 500)],)
    assert quote(*args, coupon="TENOFF") == quote(*args, coupon="TENOFF")


@pytest.mark.parametrize("qty", [0, -1, "2", 1.5, True])
def test_invalid_quantity(qty):
    with pytest.raises(ValueError, match="invalid quantity"):
        quote([L("A", qty, 100)])


@pytest.mark.parametrize("price", [-1, "100", 9.99])
def test_invalid_price(price):
    with pytest.raises(ValueError, match="invalid price"):
        quote([L("A", 1, price)])


def test_api_maps_validation_error():
    out = handle_quote(json.dumps({"lines": [{"sku": "A", "qty": 0, "unit_price": 5}]}))
    assert json.loads(out) == {"error": "invalid quantity"}


def test_api_full_response():
    out = handle_quote(
        json.dumps(
            {
                "lines": [{"sku": "A", "qty": 1, "unit_price": 1999}],
                "coupon": "SAVE5",
                "customer": {"id": "c1", "tier": "gold"},
            }
        )
    )
    assert json.loads(out) == {
        "subtotal": 1999,
        "discount": 100,
        "tax": 152,
        "total": 2051,
        "warnings": ["coupon SAVE5 requires a 20.00 minimum"],
    }
