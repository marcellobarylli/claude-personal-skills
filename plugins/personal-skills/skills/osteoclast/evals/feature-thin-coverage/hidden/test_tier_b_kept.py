"""The tax-rate environment override is something a deployment could rely on:
removing it narrows the contract, so it must survive a safe-cuts-only pass."""
import os
import subprocess
import sys


def test_env_override_still_works():
    code = (
        "from shopcart.pricing import CartLine, quote;"
        "q = quote([CartLine('A', 1, 1000)]); print(q.tax, q.total)"
    )
    env = dict(os.environ, PRICING_TAX_RATE_BPS="0")
    out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True)
    assert out.stdout.split() == ["0", "1000"]
