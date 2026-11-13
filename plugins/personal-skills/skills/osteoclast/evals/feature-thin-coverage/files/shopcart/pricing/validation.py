"""Cart validation."""


def validate_lines(lines):
    """Reject carts the web tier should never have sent."""
    for line in lines:
        if not isinstance(line.qty, int) or isinstance(line.qty, bool) or line.qty < 1:
            raise ValueError("invalid quantity")
        if not isinstance(line.unit_price, int) or isinstance(line.unit_price, bool) or line.unit_price < 0:
            raise ValueError("invalid price")
