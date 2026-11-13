"""Mutable state threaded through the strategy chain."""
from dataclasses import dataclass, field

from .money import Money


@dataclass
class PricingContext:
    lines: list
    coupon: str
    customer: object
    config: object
    subtotal: Money
    running: Money
    discounts: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    hooks: dict = field(default_factory=dict)

    def fire(self, event, strategy):
        """Notify listeners registered for ``event``."""
        for listener in self.hooks.get(event, []):
            listener(self, strategy)

    def record(self, name, amount):
        self.discounts[name] = amount
        self.running = self.running - amount
