"""Pluggable rounding policies."""
from decimal import ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from enum import Enum


class RoundingPolicy(Enum):
    HALF_UP = "half_up"
    HALF_EVEN = "half_even"
    FLOOR = "floor"


_MODES = {
    RoundingPolicy.HALF_UP: ROUND_HALF_UP,
    RoundingPolicy.HALF_EVEN: ROUND_HALF_EVEN,
    RoundingPolicy.FLOOR: ROUND_FLOOR,
}


def apply_rate(amount, bps, policy=RoundingPolicy.HALF_UP):
    """Return ``amount`` times ``bps`` basis points, rounded per ``policy``."""
    exact = Decimal(amount) * Decimal(bps) / Decimal(10000)
    return int(exact.quantize(Decimal("1"), rounding=_MODES[policy]))
