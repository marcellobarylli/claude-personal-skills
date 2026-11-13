"""Pricing configuration."""
import os
from dataclasses import dataclass

from .rounding import RoundingPolicy


@dataclass(frozen=True)
class PricingConfig:
    tax_rate_bps: int = 800
    bulk_threshold: int = 10
    bulk_rate_bps: int = 1000
    member_rate_bps: int = 500
    rounding: RoundingPolicy = RoundingPolicy.HALF_UP
    currency: str = "USD"
    cache_size: int = 128

    @classmethod
    def from_env(cls, environ=None):
        """Build a config, letting ops override the tax rate per deployment."""
        if environ is None:
            environ = os.environ
        overrides = {}
        if "PRICING_TAX_RATE_BPS" in environ:
            overrides["tax_rate_bps"] = int(environ["PRICING_TAX_RATE_BPS"])
        return cls(**overrides)
