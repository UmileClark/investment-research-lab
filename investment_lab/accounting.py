"""Independent ledger replay and exact forward price/FX decomposition."""
import numpy as np
from .data import Market, read
from .math import price_fx_attribution


def audit():
    m = Market()
    old, now = read("historical_book.json"), m.current
    units = dict.fromkeys(m.symbols, 0.)
    cash, fees, gross_pnl = 100000., 0., 0.
    trades_by_date = {}
    for t in old["trades"]:
        trades_by_date.setdefault(t["date"], []).append(t)
    previous = None
    errors = []
    for h in old["history"]:
        prices = {s: m.eur_price(m.post, s, h["date"]) for s in m.symbols}
        if previous is not None:
            gross_pnl += sum(units[s]*(prices[s]-previous[s]) for s in m.symbols)
        for t in trades_by_date.get(h["date"], []):
            s = t["ticker"]
            amount = t["indexUnits"] * prices[s]
            if abs(amount-t["amount"]) > 1e-6:
                raise ValueError("Ledger trade amount mismatch")
            fee = abs(amount) * (.005 if s in ["BTC-USD", "ETH-USD"] else .0025)
            if abs(fee-t["fee"]) > 1e-6:
                raise ValueError("Ledger fee mismatch")
            cash -= amount+fee
            fees += fee
            units[s] += t["indexUnits"]
        nav = cash+sum(units[s]*prices[s] for s in m.symbols)
        errors.append(abs(nav-h["nav"]))
        previous = prices
    for h in old["holdings"]:
        row = m.row(m.post, h["ticker"], old["end"])
        equivalent_shares = units[h["ticker"]]*row["adjusted"]/row["close"]
        if abs(equivalent_shares-h["units"]) > 1e-7:
            raise ValueError("Handover share-equivalent mismatch")
    forward = read("forward_prices.json")
    marked = now["cash"]
    for h in now["holdings"]:
        s = h["ticker"]
        fx = 1 if h["currency"] == "EUR" else 1/m.row(forward, "EURUSD=X", now["asof"], exact=True)["close"]
        marked += h["units"]*m.row(forward, s, now["asof"], exact=True)["close"]*fx
        if h["units"] > 0:
            events = [e for e in forward[s]["events"] if old["end"] < e["date"] <= now["asof"]]
            if events:
                raise ValueError("Corporate action needs explicit reconciliation")
    source_dates = {s[0]: s[2] for s in m.book["sources"]}
    for j in m.book["journal"]:
        if any(source_dates[s] > j["date"] for s in j["sources"]):
            raise ValueError("Future evidence attached to historical decision")
        if j["execute"] and j["date"] >= j["execute"]:
            raise ValueError("Decision must precede fill")
    if now["pending"]["fills"] or now["pending"]["actualExecutionDate"] is not None:
        raise ValueError("Frozen pending order must remain unfilled")
    identity_error = gross_pnl-fees-(nav-100000)
    assert max(errors) < 1e-6 and abs(marked-now["nav"]) < 1e-6 and abs(identity_error) < 1e-6
    return {"historical_nav":nav,"current_nav":marked,"cash":cash,"fees":fees,
            "gross_price_fx_pnl":gross_pnl,"net_historical_pnl":nav-100000,
            "max_daily_nav_error_eur":max(errors),"pnl_identity_error_eur":identity_error,
            "daily_marks":len(errors),"transactions":len(old["trades"]),
            "allocation_dates":len(old["rebalances"]),"pending_excluded":True,
            "historical_units":"Adjusted total-return index units; handover converts to share equivalents",
            "limitation":"Replay validates accounting, not historical authorship or achievable fills. No tax; zero cash interest."}


def attribution():
    m = Market()
    old = {h["ticker"]:h for h in read("historical_book.json")["holdings"]}
    rows = []
    for h in m.current["holdings"]:
        b = old[h["ticker"]]
        local, fx = price_fx_attribution(h["units"],b["price"],h["price"],b["fx"],h["fx"])
        total = h["value"]-b["value"]
        assert abs(local+fx-total) < 1e-7
        rows.append({"ticker":h["ticker"],"local_price_eur":local,"fx_eur":fx,"total_eur":total})
    totals = {k:sum(r[k] for r in rows) for k in ["local_price_eur","fx_eur","total_eur"]}
    assert abs(totals["total_eur"]-m.current["forwardPnl"]) < 1e-6
    return {"start":"2026-09-18","end":m.current["asof"],"rows":rows,"totals":totals,
            "formula":"q*(P1-P0)*X0 + q*P1*(X1-X0), X = EUR per local currency",
            "convention":"Interaction allocated to FX; fixed units, no intervening distributions or trades",
            "usd_quoted_weight":sum(h["weight"] for h in m.current["holdings"] if h["currency"]=="USD"),
            "limitation":"Quotation-currency exposure is not underlying economic currency exposure; VT and ADRs contain other currencies."}
