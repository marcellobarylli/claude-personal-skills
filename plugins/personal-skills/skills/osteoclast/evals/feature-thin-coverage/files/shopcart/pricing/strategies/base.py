"""Strategy interface."""
from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """A single step in the discount chain. Lower priority runs first."""

    name = "base"
    priority = 100

    @abstractmethod
    def applies(self, ctx):
        """Whether this strategy should run for the given context."""

    @abstractmethod
    def compute(self, ctx):
        """Return the discount as Money."""
