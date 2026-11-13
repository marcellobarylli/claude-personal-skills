from ..money import Money
from .base import DiscountStrategy

SAVE5_AMOUNT = 500
SAVE5_MINIMUM = 2000
TENOFF_BPS = 1000


class CouponStrategy(DiscountStrategy):
    name = "coupon"
    priority = 20

    def applies(self, ctx):
        return bool(ctx.coupon)

    def compute(self, ctx):
        currency = ctx.config.currency
        code = ctx.coupon
        if code == "SAVE5":
            if ctx.running >= Money(SAVE5_MINIMUM, currency):
                return Money(SAVE5_AMOUNT, currency)
            ctx.warnings.append("coupon SAVE5 requires a 20.00 minimum")
            return Money.zero(currency)
        if code == "TENOFF":
            return ctx.running.percent(TENOFF_BPS, ctx.config.rounding)
        ctx.warnings.append(f"unknown coupon: {code}")
        return Money.zero(currency)
