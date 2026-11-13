from ..money import Money
from .base import DiscountStrategy


class MemberDiscountStrategy(DiscountStrategy):
    name = "member"
    priority = 30

    def applies(self, ctx):
        # Guard against anonymous checkouts
        if ctx.customer is None:
            return False
        return getattr(ctx.customer, "tier", None) == "gold"

    def compute(self, ctx):
        if ctx.customer is None:
            return Money.zero(ctx.config.currency)
        return ctx.running.percent(ctx.config.member_rate_bps, ctx.config.rounding)
