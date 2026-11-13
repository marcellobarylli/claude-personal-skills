"""Currency-aware money value object."""
from .rounding import RoundingPolicy, apply_rate


class CurrencyMismatchError(ValueError):
    pass


class Money:
    """An integer amount of minor units in a given currency."""

    __slots__ = ("amount", "currency")

    def __init__(self, amount, currency="USD"):
        self.amount = int(amount)
        self.currency = currency

    def _check(self, other):
        if not isinstance(other, Money):
            raise TypeError("can only combine Money with Money")
        if other.currency != self.currency:
            raise CurrencyMismatchError(f"{self.currency} vs {other.currency}")

    def __add__(self, other):
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __eq__(self, other):
        return isinstance(other, Money) and (self.amount, self.currency) == (other.amount, other.currency)

    def __lt__(self, other):
        self._check(other)
        return self.amount < other.amount

    def __ge__(self, other):
        self._check(other)
        return self.amount >= other.amount

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"

    def percent(self, bps, policy=RoundingPolicy.HALF_UP):
        return Money(apply_rate(self.amount, bps, policy), self.currency)

    @classmethod
    def zero(cls, currency="USD"):
        return cls(0, currency)
