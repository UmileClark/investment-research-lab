"""Descriptive market-model event studies, selected retrospectively."""
import numpy as np
from .data import Market


def estimate(dates, prices, day, estimation=(-120,-21), window=(-5,5)):
    ret=prices[1:]/prices[:-1]-1;rd=dates[1:]
    if day not in rd:raise ValueError("Event has no common quote")
    idx=rd.index(day)
    a,b=idx+estimation[0],idx+estimation[1]+1
    if a<0 or idx+window[1]>=len(ret):raise ValueError("Insufficient event window")
    x=np.column_stack([np.ones(b-a),ret[a:b,1]])
    beta=np.linalg.lstsq(x,ret[a:b,0],rcond=None)[0]
    residual=ret[a:b,0]-x@beta
    rows=[];car=0.
    for offset in range(window[0],window[1]+1):
        i=idx+offset;expected=beta[0]+beta[1]*ret[i,1]
        abnormal=ret[i,0]-expected;car+=abnormal
        rows.append({"day":offset,"date":rd[i],"stock_return":float(ret[i,0]),"market_return":float(ret[i,1]),
                     "abnormal_return":float(abnormal),"cumulative_abnormal_return":float(car)})
    return {"alpha_daily":float(beta[0]),"beta":float(beta[1]),"estimation_start":rd[a],"estimation_end":rd[b-1],
            "estimation_n":b-a,"residual_daily_vol":float(np.std(residual,ddof=2)),"rows":rows,
            "car_minus5_plus5":float(car),"event_day_abnormal_return":next(r["abnormal_return"] for r in rows if r["day"]==0)}


def run():
    m=Market();out=[]
    for ticker,benchmark,day,source,label in [("NVO","VT","2024-12-20","novoTrial","REDEFINE 1 headline readout"),
                                            ("NVO","VT","2025-07-29","novo25","Novo guidance revision"),
                                            ("RHM.DE","IEUR","2025-03-12","rhm25","Rheinmetall results and outlook")]:
        dates,p=m.panel(m.combined,"2021-09-27","2026-09-18",[ticker,benchmark])
        out.append({"ticker":ticker,"benchmark":benchmark,"event_date":day,"source_id":source,"event":label,**estimate(dates,p,day)})
    return {"events":out,"price_archive_bridge":m.bridge,
            "formula":"r_stock = alpha + beta*r_benchmark + residual; OLS fit on sessions [-120,-21], CAR=sum(abnormal returns)",
            "limitation":"Three events selected after observing outcomes; descriptive, not causal inference or strategy validation. Concurrent news, EUR translation and asynchronous Europe/US closes matter. No significance claim, multiple-testing adjustment or sector-factor model."}
