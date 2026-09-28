"""Carry mechanics and spot-only risk. Never manufactures a carry backtest."""
import numpy as np
from .data import Market
from .math import carry_pnl, carry_break_even, tail_risk


def run():
    m=Market()
    scenarios=[]
    # September-2024 policy-rate anchors used as illustrative deposits/loans.
    # They are not tradable forward quotes, actual funding or current rates.
    for pair,target,funding in [("AUDJPY",.0435,.0025),("MXNJPY",.105,.0025)]:
        for spot in [-.15,-.10,-.05,0,.05]:
            scenarios.append({"pair":pair,"target_rate":target,"funding_rate":funding,"years":.25,
                              "spot_return":spot,"pnl_per_borrowed_notional":carry_pnl(target,funding,.25,spot,.001)})
    details=[]
    for pair,target in [("AUDJPY",.0435),("MXNJPY",.105)]:
        spot_rows=[r for r in m.post[pair+"=X"]["rows"] if "2024-09-30"<=r["date"]<="2026-09-18"]
        p=np.array([r["close"] for r in spot_rows]);r=p[1:]/p[:-1]-1
        var,es,n=tail_risk(r)
        details.append({"pair":pair,"break_even_spot_return":carry_break_even(target,.0025,.25,.001),
                        "flat_spot_quarter_pnl":carry_pnl(target,.0025,.25,0,.001),
                        "costless_forward_ratio":(1+.0025*.25)/(1+target*.25),
                        "spot_observations":len(r),"daily_spot_var975":var,"daily_spot_es975":es,"tail_n":n,
                        "worst_daily_spot_return":float(r.min()),"spot_start":spot_rows[0]["date"],"spot_end":spot_rows[-1]["date"]})
    ar={x["date"]:x["close"] for x in m.post["AUDJPY=X"]["rows"]};mr={x["date"]:x["close"] for x in m.post["MXNJPY=X"]["rows"]}
    dates=sorted(d for d in set(ar)&set(mr) if "2024-09-30"<=d<="2026-09-18")
    p=np.array([[ar[d],mr[d]] for d in dates]);r=p[1:]/p[:-1]-1
    return {"pairs":details,"scenarios":scenarios,"daily_spot_correlation":float(np.corrcoef(r.T)[0,1]),
            "funded_portfolio_exposure":0,"formula":"(1+r_target*T)*(S1/S0) - (1+r_JPY*T) - cost; S=JPY per target unit",
            "limitation":"Hypothetical simple-interest deposits; no forward points, cross-currency basis, margin path, broker financing, or EUR conversion. Spot risk is not total carry P&L. Both pairs share JPY funding."}
