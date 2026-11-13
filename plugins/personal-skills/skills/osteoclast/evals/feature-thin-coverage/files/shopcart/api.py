import json

from .pricing import CartLine, Customer, quote


def handle_quote(payload):
    """Entry point for the web tier: JSON string in, JSON string out."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return json.dumps({"error": "invalid json"})
    try:
        lines = [CartLine(item["sku"], item["qty"], item["unit_price"]) for item in data.get("lines", [])]
        customer = Customer(**data["customer"]) if data.get("customer") else None
        result = quote(lines, coupon=data.get("coupon"), customer=customer)
    except (KeyError, TypeError):
        return json.dumps({"error": "bad request"})
    except ValueError as exc:
        return json.dumps({"error": str(exc)})
    return json.dumps(
        {
            "subtotal": result.subtotal,
            "discount": result.discount,
            "tax": result.tax,
            "total": result.total,
            "warnings": list(result.warnings),
        }
    )
