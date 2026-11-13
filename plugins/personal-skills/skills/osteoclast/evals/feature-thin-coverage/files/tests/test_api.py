import json

from shopcart.api import handle_quote


def test_roundtrip():
    out = json.loads(handle_quote(json.dumps({"lines": [{"sku": "A", "qty": 1, "unit_price": 500}]})))
    assert out["total"] == 540
