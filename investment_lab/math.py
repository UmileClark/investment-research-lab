"""Small, tested financial primitives. All rates are decimal annual rates."""
import math
import numpy as np


def covariance(returns, shrinkage=.25, target_type="constant_correlation"):
    if not 0 <= shrinkage <= 1:
        raise ValueError("Shrinkage must be between zero and one")
    sample = np.cov(returns, rowvar=False, ddof=1) * 252
    vol = np.sqrt(np.diag(sample))
    if np.any(vol <= 0):
        raise ValueError("Constant series cannot be standardised")
    corr = sample / np.outer(vol, vol)
    n = len(vol)
    rho = (corr.sum() - n) / (n * (n - 1))
    target = rho * np.outer(vol, vol)
    np.fill_diagonal(target, np.diag(sample))
    if target_type == "diagonal":
        target = np.diag(np.diag(sample))
    elif target_type != "constant_correlation":
        raise ValueError("Unknown covariance target")
    return (1 - shrinkage) * sample + shrinkage * target


def risk_contributions(weights, cov):
    variance = float(weights @ cov @ weights)
    if variance <= 0:
        raise ValueError("Portfolio variance must be positive")
    return math.sqrt(variance), weights * (cov @ weights) / variance


def tail_risk(returns, tail=.025):
    if not 0 < tail < .5:
        raise ValueError("Invalid tail probability")
    losses = np.sort(-np.asarray(returns))
    count = max(1, math.ceil(len(losses) * tail))
    return float(np.quantile(losses, 1-tail)), float(losses[-count:].mean()), count


def block_bootstrap_vol(returns, runs=1000, block=10, seed=20260928):
    """Circular moving blocks preserve short dependence, not regime changes."""
    rng = np.random.default_rng(seed)
    n = len(returns)
    out = []
    for _ in range(runs):
        starts = rng.integers(0, n, math.ceil(n / block))
        idx = ((starts[:, None] + np.arange(block)) % n).ravel()[:n]
        out.append(float(np.std(returns[idx], ddof=1) * math.sqrt(252)))
    return np.quantile(out, [.025, .5, .975]).tolist()


def bond_price(coupon, ytm, years, face=100, frequency=2):
    if years <= 0 or ytm <= -frequency or int(years * frequency) != years * frequency:
        raise ValueError("Invalid bond terms")
    t = np.arange(1, int(years * frequency) + 1)
    cf = np.full(len(t), face * coupon / frequency)
    cf[-1] += face
    return float(np.sum(cf / (1 + ytm / frequency) ** t))


def bond_greeks(coupon, ytm, years):
    h = .0001
    p = bond_price(coupon, ytm, years)
    up = bond_price(coupon, ytm+h, years)
    down = bond_price(coupon, ytm-h, years)
    return {"price": p, "duration": (down-up)/(2*h*p), "convexity": (up+down-2*p)/(h*h*p)}


def equity_dcf(cash, growth, discount, terminal, years=5):
    if cash <= 0 or discount <= terminal or min(growth, discount, terminal) <= -1:
        raise ValueError("Positive cash and discount > terminal growth required")
    explicit = sum(cash*(1+growth)**t/(1+discount)**t for t in range(1, years+1))
    tv = cash*(1+growth)**years*(1+terminal)/(discount-terminal)/(1+discount)**years
    return explicit+tv, tv/(explicit+tv)


def reverse_dcf(cash, price, discount, terminal):
    lo, hi = -.9, 2.
    if not equity_dcf(cash, lo, discount, terminal)[0] <= price <= equity_dcf(cash, hi, discount, terminal)[0]:
        raise ValueError("Price outside growth search bounds")
    for _ in range(100):
        mid = (lo+hi)/2
        if equity_dcf(cash, mid, discount, terminal)[0] > price:
            hi = mid
        else:
            lo = mid
    return (lo+hi)/2


def carry_pnl(target_rate, funding_rate, years, spot_return, cost=0.):
    """JPY P&L / initial JPY borrowed; spot quote JPY per target currency.

    Not a return on margin or a EUR portfolio return. Positive spot_return means
    the target currency appreciates against JPY. Simple interest, no rollover.
    """
    return (1+target_rate*years)*(1+spot_return) - (1+funding_rate*years) - cost


def carry_break_even(target_rate, funding_rate, years, cost=0.):
    return (1+funding_rate*years+cost)/(1+target_rate*years)-1


def price_fx_attribution(units, p0, p1, fx0, fx1):
    local = units*(p1-p0)*fx0
    currency = units*p1*(fx1-fx0)  # interaction assigned explicitly to FX
    return local, currency
