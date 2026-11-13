from shopcart.pricing import CartLine, Customer, quote


def test_simple_quote():
    q = quote([CartLine("A", 2, 1000)])
    assert (q.subtotal, q.discount, q.tax, q.total) == (2000, 0, 160, 2160)


def test_gold_member():
    q = quote([CartLine("A", 2, 1000)], customer=Customer("c1", "gold"))
    assert (q.discount, q.total) == (100, 2052)
