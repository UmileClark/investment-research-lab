"""EUR/USD translation-hedge sensitivity, with explicit forward drag assumptions."""
import numpy as np
from .analytics import sample, stats, result


def minimum_variance_ratio(asset_returns, hedge_returns):
    return float(np.cov(asset_returns,hedge_returns,ddof=1)[0,1]/np.var(hedge_returns,ddof=1))


def run():
    m,dates,p,r,w=sample(); usd=np.array([m.currency[s]=="USD" for s in m.symbols]); exposure=float(w[usd].sum())
    fx=np.array([1/m.row(m.combined,"EURUSD=X",d,True)["close"] for d in dates]); x=fx[1:]/fx[:-1]-1
    basket=r@w; hedge=exposure*x
    train=np.array([d<="2024-09-27" for d in dates[1:]]); test=~train
    raw=minimum_variance_ratio(basket[train],hedge[train]); clipped=float(np.clip(raw,0,1))
    rows=[]
    for label,h in [("No hedge",0.),("Half hedge",.5),("Full opening-notional hedge",1.),("Training minimum variance (bounded)",clipped)]:
        for drag in [0.,.01,.03]:
            rr=basket[test]-h*hedge[test]-h*exposure*drag/252
            rows.append({"policy":label,"hedge_ratio":h,"annual_hedge_drag":drag,"usd_listing_weight":exposure,**stats(rr)})
    show=[a for a in rows if a["annual_hedge_drag"]==.01]
    return result(f"USD-listed positions are {exposure:.1%} of NAV. A training-window minimum-variance translation hedge is {raw:.1%} before the 0–100% bound; this is not an economic currency look-through.",
        {"hedge_sensitivity":rows,"calibration":[{"training_start":dates[1],"training_end":"2024-09-27","evaluation_start":np.array(dates[1:])[test][0],"evaluation_end":dates[-1],"raw_ratio":raw,"bounded_ratio":clipped}]},
        {"kind":"bar","labels":[a["policy"] for a in show],"values":[100*a["annual_vol"] for a in show],"ylabel":"Annualised EUR volatility (%)","title":"Opening-notional FX hedge · assumed 1% annual drag"},
        ["Current 25 September weights applied to past returns; hypothetical daily constant weights.","Hedge payoff is -h × starting USD-listed weight × change in EUR per USD.","0%, 1% and 3% annual drag are sensitivity assumptions, not observed forward points. No dollar cash position exists in the base book."],
        "This is a translation counterfactual, not a funded forward strategy. The hedge covers opening dollar notional, leaving asset-return × FX interaction. Daily resetting, margin, basis and executable spreads are omitted. VT, IEUR, ADRs and commodities have economic exposures different from their listing currency; a universal USD hedge can introduce new risk.")
