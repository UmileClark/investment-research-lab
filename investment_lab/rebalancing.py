"""Chronological rule comparison. No return-driven parameter selection."""
from datetime import date, timedelta
import numpy as np
from .data import Market, settings


def month_review(day):
    """Last weekday of a month; exchange holidays are handled by available closes.

    Only the calendar is inspected. If this weekday is a missing common-market
    holiday, the review is skipped, not shifted with future price information.
    """
    d=date.fromisoformat(day)
    nxt=d+timedelta(days=1)
    while nxt.weekday()>=5:nxt+=timedelta(days=1)
    return nxt.month != d.month


def simulate(dates, prices, targets, costs, mode, absolute=.01, relative=.25):
    if mode not in ["buy_hold","monthly","drift"]:
        raise ValueError("Unknown rule")
    units=np.zeros(len(targets));cash=100000.;fees=0.;turnover=0.;history=[];trades=[]
    pending=None
    for i,day in enumerate(dates):
        p=prices[i];nav=float(cash+units@p)
        if i==0 or pending is not None:
            before=nav
            new=nav*targets/p
            amounts=(new-units)*p
            cost=float(abs(amounts)@costs)
            cash-=float(amounts.sum())+cost
            if cash < -1e-7:raise ValueError("Negative cash")
            units=new;fees+=cost;turnover+=float(abs(amounts).sum()/before)
            trades.append({"decision_date":"2024-09-27" if i==0 else pending,
                           "fill_date":day,"fees":cost,"gross_traded_eur":float(abs(amounts).sum()),
                           "amounts":amounts.tolist()})
            pending=None
            nav=float(cash+units@p)
        history.append({"date":day,"nav":nav})
        if mode != "buy_hold" and month_review(day):
            drift=abs(units*p/nav-targets)
            if mode=="monthly" or np.any(drift>=np.maximum(absolute,relative*targets)):
                pending=day  # Executed only when a strictly later close arrives.
    vals=np.array([100000.]+[h["nav"] for h in history])
    returns=vals[1:]/vals[:-1]-1
    elapsed=(date.fromisoformat(dates[-1])-date.fromisoformat(dates[0])).days/365.25
    return {"rule":mode,"nav":float(vals[-1]),"total_return":float(vals[-1]/100000-1),
            "cagr":float((vals[-1]/100000)**(1/elapsed)-1),
            "max_drawdown":float(np.min(vals/np.maximum.accumulate(vals)-1)),
            "annualised_volatility":float(np.std(returns,ddof=1)*np.sqrt(252)),
            "fees":fees,"gross_turnover_nav_multiple":turnover,"allocation_dates":len(trades),
            "unfilled_review":pending,"history":history,"trades":trades}


def run():
    m=Market();cfg=settings()
    dates,p=m.panel(m.post,cfg["study_start"],cfg["study_end"])
    costs=np.array([.005 if s in ["BTC-USD","ETH-USD"] else .0025 for s in m.symbols])
    results=[simulate(dates,p,m.weights,costs,mode,cfg["drift_absolute"],cfg["drift_relative"])
             for mode in ["buy_hold","monthly","drift"]]
    cost_grid=[]
    for mult in [0,.5,1,2]:
        for mode in ["buy_hold","monthly","drift"]:
            r=simulate(dates,p,m.weights,costs*mult,mode)
            cost_grid.append({"cost_multiplier":mult,"rule":mode,"nav":r["nav"],"fees":r["fees"]})
    return {"start":dates[0],"end":dates[-1],"symbols":m.symbols,"results":results,"cost_sensitivity":cost_grid,
            "signal":"Last calendar weekday close, monthly review; next available common-market close execution. Missing review-date quote skips that review.",
            "universe":"All 16 funded instruments at September-2024 inception; fixed initial target weights for every rule",
            "limitation":"Rules and universe specified in 2026 with knowledge of the historical period. Chronological execution prevents one leakage mechanism but does not create a genuine out-of-sample test. No claim of optimality; no tax, cash yield, intraday slippage or exchange-synchronous fills."}
