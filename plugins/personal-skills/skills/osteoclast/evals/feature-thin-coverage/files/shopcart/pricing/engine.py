"""Quote engine."""
from .cache import QuoteCache
from .config import PricingConfig
from .context import PricingContext
from .models import Quote
from .money import Money
from .strategies import default_strategies
from .validation import validate_lines

_CACHE = QuoteCache()


class PricingEngine:
    def __init__(self, config=None, strategies=None, cache=None):
        self.config = config if config is not None else PricingConfig()
        self.strategies = sorted(
            strategies if strategies is not None else default_strategies(),
            key=lambda strategy: strategy.priority,
        )
        self.cache = cache
        self._hooks = {"before_strategy": [], "after_strategy": []}

    def register_hook(self, event, listener):
        """Register a listener for ``before_strategy`` or ``after_strategy``."""
        if event not in self._hooks:
            raise ValueError(f"unknown event: {event}")
        self._hooks[event].append(listener)

    def _cache_key(self, lines, coupon, customer):
        tier = customer.tier if customer is not None else None
        return (
            tuple((line.sku, line.qty, line.unit_price) for line in lines),
            coupon,
            tier,
            self.config.tax_rate_bps,
        )

    def price(self, lines, coupon=None, customer=None):
        # Normalise inputs
        if lines is None:
            lines = []
        lines = list(lines)
        coupon = (coupon or "").strip().upper()

        # Validate the cart
        validate_lines(lines)

        # Check the cache
        key = self._cache_key(lines, coupon, customer)
        if self.cache is not None:
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        # Build the context
        currency = self.config.currency
        subtotal = Money(sum(line.qty * line.unit_price for line in lines), currency)
        ctx = PricingContext(
            lines=lines,
            coupon=coupon,
            customer=customer,
            config=self.config,
            subtotal=subtotal,
            running=subtotal,
            hooks=self._hooks,
        )

        # Run the strategy chain
        for strategy in self.strategies:
            if not strategy.applies(ctx):
                continue
            ctx.fire("before_strategy", strategy)
            ctx.record(strategy.name, strategy.compute(ctx))
            ctx.fire("after_strategy", strategy)

        # Never let the total go negative
        if ctx.running < Money.zero(currency):
            ctx.running = Money.zero(currency)

        # Compute tax and assemble the quote
        tax = ctx.running.percent(self.config.tax_rate_bps, self.config.rounding)
        result = Quote(
            subtotal=subtotal.amount,
            discount=(subtotal - ctx.running).amount,
            tax=tax.amount,
            total=(ctx.running + tax).amount,
            warnings=tuple(ctx.warnings),
        )

        # Store in the cache
        if self.cache is not None:
            self.cache.put(key, result)
        return result


def quote(lines, coupon=None, customer=None):
    """Price a cart. This is the function the rest of the app calls."""
    engine = PricingEngine(config=PricingConfig.from_env(), cache=_CACHE)
    return engine.price(lines, coupon=coupon, customer=customer)
