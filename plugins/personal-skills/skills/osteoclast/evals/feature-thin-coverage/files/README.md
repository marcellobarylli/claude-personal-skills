# shopcart

Cart pricing for the storefront. The web tier calls `shopcart.api.handle_quote(json_string)`;
everything else is internal.

Pricing rules, all amounts in integer cents:

1. A line with 10 or more units gets 10% off that line.
2. A coupon applies next: `SAVE5` takes 5.00 off carts of 20.00 or more, `TENOFF` takes 10% off.
3. Gold members get 5% off what is left.
4. Tax is 8% of the discounted amount.

Run the tests with `python -m pytest -q`.
