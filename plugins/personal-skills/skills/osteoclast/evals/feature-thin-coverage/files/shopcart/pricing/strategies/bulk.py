from ..money import Money
from .base import DiscountStrategy


class BulkDiscountStrategy(DiscountStrategy):
    name = "bulk"
    priority = 10

    def applies(self, ctx):
        return any(line.qty >= ctx.config.bulk_threshold for line in ctx.lines)

    def compute(self, ctx):
        total = Money.zero(ctx.config.currency)
        for line in ctx.lines:
            # Skip lines with a non-positive quantity
            if line.qty <= 0:
                continue
            if line.qty >= ctx.config.bulk_threshold:
                line_total = Money(line.qty * line.unit_price, ctx.config.currency)
                total = total + line_total.percent(ctx.config.bulk_rate_bps, ctx.config.rounding)
        return total
