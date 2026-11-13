from .bulk import BulkDiscountStrategy
from .coupon import CouponStrategy
from .member import MemberDiscountStrategy


def default_strategies():
    return [BulkDiscountStrategy(), CouponStrategy(), MemberDiscountStrategy()]
