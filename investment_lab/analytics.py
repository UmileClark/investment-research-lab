"""Shared diagnostics; every historical return is in EUR unless stated otherwise."""
from datetime import date
import math
import numpy as np
from .data import Market, settings
from .rebalancing import month_review


def sample(start="2021-09-27", end=None):
    m = Market()
    dates, prices = m.panel(m.combined, start, end or settings()["study_end"])
    returns = prices[1:] / prices[:-1] - 1
    weights = np.array([next(h["weight"] for h in m.current["holdings"] if h["ticker"] == s) for s in m.symbols])
    return m, dates, prices, returns, weights


def stats(returns):
    r = np.asarray(returns, dtype=float)
    wealth = np.r_[1., np.cumprod(1 + r)]
    dd = wealth / np.maximum.accumulate(wealth) - 1
    losses = np.sort(-r)
    return {"total_return": float(wealth[-1]-1), "annual_vol": float(r.std(ddof=1)*np.sqrt(252)),
            "max_drawdown": float(dd.min()), "daily_es975": float(losses[-max(1, math.ceil(.025*len(r))):].mean())}


def nw_ols(y, x, lags=5):
    """OLS plus Bartlett/Newey-West covariance, no finite-sample t claims."""
    y, x = np.asarray(y), np.asarray(x)
    design = np.column_stack([np.ones(len(y)), x])
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    resid = y-design@beta
    scores = design*resid[:, None]
    meat = scores.T@scores
    for lag in range(1, min(lags, len(y)-1)+1):
        gamma = scores[lag:].T@scores[:-lag]
        meat += (1-lag/(lags+1))*(gamma+gamma.T)
    bread = np.linalg.pinv(design.T@design)
    variance = bread@meat@bread
    se = np.sqrt(np.maximum(np.diag(variance), 0))
    r2 = 1-float(resid@resid)/float(np.sum((y-y.mean())**2))
    return beta, se, r2, resid


def target_at(prices, i, base, mode, lookback=252, target_vol=.10):
    """Only prices through i enter a signal, which may fill at i+1 or later."""
    if mode == "baseline": return base.copy()
    if mode == "trend":
        if i < lookback: raise ValueError("Insufficient trend lookback")
        return base*(prices[i]/prices[i-lookback] > 1)
    if mode == "volcontrol":
        if i < 60: raise ValueError("Insufficient volatility lookback")
        r = prices[i-59:i+1]/prices[i-60:i]-1
        vol = float(np.std(r@base, ddof=1)*np.sqrt(252))
        return base*np.clip(target_vol/max(vol, 1e-8), .25, 1.)
    raise ValueError("Unknown strategy")


def policy_simulation(dates, prices, base, costs, mode, start="2024-09-30", lookback=252, target_vol=.10):
    """Cash-funded units, fees on both legs; signals and fills are separated."""
    first = next(i for i,d in enumerate(dates) if d >= start)
    if first < max(60, lookback if mode == "trend" else 0): raise ValueError("Training window unavailable")
    units = np.zeros(len(base)); cash = 100000.; fees = 0.; turnover = 0.
    pending = (dates[first-1], target_at(prices, first-1, base, mode, lookback, target_vol))
    history, trades = [], []
    for i in range(first, len(dates)):
        day, price = dates[i], prices[i]
        nav = float(cash+units@price)
        if pending:
            signal_day, targets = pending
            if signal_day >= day: raise ValueError("Signal must precede fill")
            new_units = nav*targets/price
            amounts = (new_units-units)*price
            fee = float(np.abs(amounts)@costs)
            cash -= float(amounts.sum())+fee
            if cash < -1e-7: raise ValueError("Insufficient cash for costs")
            units = new_units; fees += fee; turnover += float(np.abs(amounts).sum()/nav)
            trades.append({"signal_date":signal_day,"fill_date":day,"fee_eur":fee,"risky_target":float(targets.sum())})
            pending = None
        nav = float(cash+units@price)
        history.append({"date":day,"nav":nav,"risky_weight":float(units@price/nav)})
        if month_review(day): pending = (day, target_at(prices,i,base,mode,lookback,target_vol))
    navs = np.array([100000.]+[h["nav"] for h in history])
    result = stats(navs[1:]/navs[:-1]-1)
    return {"policy":mode,**result,"fees_eur":fees,"gross_turnover":turnover,"fills":len(trades),
            "history":history,"trades":trades,"unfilled_signal":pending[0] if pending else None}


def costs_for(symbols, multiplier=1):
    return np.array([.005 if s in ["BTC-USD","ETH-USD"] else .0025 for s in symbols])*multiplier


def compact(result):
    return {k:v for k,v in result.items() if k not in ["history","trades"]}


def result(summary, tables, chart, inputs, limitation):
    return {"authored":"2026-10-03","summary":summary,"tables":tables,"chart":chart,
            "inputs":inputs,"limitation":limitation}
