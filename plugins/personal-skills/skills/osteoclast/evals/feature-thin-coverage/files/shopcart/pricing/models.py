from dataclasses import dataclass


@dataclass(frozen=True)
class CartLine:
    sku: str
    qty: int
    unit_price: int  # cents


@dataclass(frozen=True)
class Customer:
    id: str
    tier: str = "standard"


@dataclass(frozen=True)
class Quote:
    subtotal: int
    discount: int
    tax: int
    total: int
    warnings: tuple = ()
