"""Transparent joint shocks. Scenarios are assumptions, never forecasts."""
from .data import read
from .analytics import result

SCENARIOS = [
    ("Growth shock", -.25, -.30, -100, .10, -.15, -.30, -.40, .08),
    ("Inflation shock", -.18, -.22, 150, .05, -.10, .35, -.35, -.05),
    ("Liquidity shock", -.30, -.40, 75, -.15, -.35, -.35, -.60, .12),
    ("EUR appreciation", 0., 0., 0, 0., 0., 0., 0., -.15),
]


def combined_return(local_return, fx_return):
    if min(local_return, fx_return) <= -1: raise ValueError("Invalid shock")
    return (1+local_return)*(1+fx_return)-1


def run():
    c = read("current_book.json"); totals=[]; details=[]; assumptions=[]
    for name, equity, single, bp, gold, silver, oil, crypto, usd in SCENARIOS:
        total=0.
        for h in c["holdings"]:
            s=h["ticker"]
            if h["asset"] == "Index equities": local=equity
            elif h["asset"] == "Single stocks": local=single
            elif s in ["IEF","SHY"]:
                duration, convexity = (7.2, 60.) if s=="IEF" else (1.8, 4.)
                local=-duration*bp/10000+.5*convexity*(bp/10000)**2
            elif s=="GLD": local=gold
            elif s=="SLV": local=silver
            elif s=="BNO": local=oil
            elif s=="CPER": local=silver
            else: local=crypto
            fx=usd if h["currency"]=="USD" else 0.
            ret=combined_return(local,fx); contribution=h["weight"]*ret; total+=contribution
            details.append({"scenario":name,"ticker":s,"local_return":local,"fx_return":fx,"eur_return":ret,"nav_contribution":contribution,"pnl_eur":contribution*c["nav"]})
        totals.append({"scenario":name,"portfolio_return":total,"pnl_eur":total*c["nav"],"ending_nav_eur":c["nav"]*(1+total)})
        assumptions.append({"scenario":name,"equity_return":equity,"single_stock_return":single,"yield_shock_bp":bp,"gold_return":gold,"silver_copper_return":silver,"oil_return":oil,"crypto_return":crypto,"usd_in_eur_return":usd})
    worst=min(totals,key=lambda r:r["portfolio_return"])
    return result(f"The assumed {worst['scenario'].lower()} produces {worst['portfolio_return']:.1%} ({worst['pnl_eur']:,.0f} EUR) on the 25 September book. This is a scenario, not a probability or VaR estimate.",
        {"scenarios":totals,"assumptions":assumptions,"position_impacts":details},
        {"kind":"bar","labels":[x["scenario"] for x in totals],"values":[100*x["portfolio_return"] for x in totals],"ylabel":"Assumed EUR portfolio return (%)","title":"Joint asset and currency shocks · current frozen weights"},
        ["Weights and NAV: 25 September 2026; cash unchanged; no pending fill.","USD shock means change in EUR per USD. Asset and FX effects compound, including the cross term.","IEF/SHY durations 7.2/1.8 and convexities 60/4 are teaching assumptions, not current fund analytics."],
        "Stress severities are chosen assumptions. Applying a common listing-currency shock can double-count economic FX exposures embedded in global assets. Nonlinear rate approximation, no dynamic hedge, liquidity haircut, counterparty default, tax or future cash flows. This does not claim to reproduce a particular crisis or regulatory stress test.")
