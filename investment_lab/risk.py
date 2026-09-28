"""Sensitivity of allocation risk to covariance assumptions and sample dates."""
import numpy as np
from .data import Market, settings
from .math import covariance, risk_contributions, tail_risk, block_bootstrap_vol


def run():
    m, cfg = Market(), settings()
    dates, p = m.training()
    r = p[1:]/p[:-1]-1
    current = {h["ticker"]:h["weight"] for h in m.current["holdings"]}
    w = np.array([current[s] for s in m.symbols])
    cov = covariance(r, 0)
    vol, rc = risk_contributions(w, cov)
    var, es, n = tail_risk(r@w, cfg["tail_probability"])
    recent_dates, recent_p = m.panel(m.combined, "2025-09-18", "2026-09-18")
    recent_r = recent_p[1:]/recent_p[:-1]-1
    recent_vol, recent_rc = risk_contributions(w, covariance(recent_r, 0))
    ci = block_bootstrap_vol(r@w, cfg["bootstrap_runs"],cfg["block_length"],cfg["seed"])
    return {"training_start":dates[0],"training_end":dates[-1],"observations":len(r),
            "weights_asof":m.current["asof"],"annualised_volatility":vol,
            "sample_volatility":float(np.std(r@w,ddof=1)*np.sqrt(252)),
            "daily_var975":var,"daily_es975":es,"tail_observations":n,
            "sample_vol_bootstrap95":ci,"bootstrap_runs":cfg["bootstrap_runs"],"block_days":cfg["block_length"],
            "recent_window_start":recent_dates[0],"recent_window_end":recent_dates[-1],"recent_volatility":recent_vol,
            "primary_estimator":"Sample covariance; shrinkage targets are sensitivity diagnostics only",
            "sensitivity":[{"target":t,"lambda":a,"volatility":risk_contributions(w,covariance(r,a,t))[0]} for t in ["constant_correlation","diagonal"] for a in [0,.25,.5,1]],
            "rows":[{"ticker":s,"weight":w[i],"risk_share":rc[i],"recent_risk_share":recent_rc[i]} for i,s in enumerate(m.symbols)],
            "limitation":"Current weights on old returns are a historical stress lens, not a 2024 forecast. Ledoit-Wolf explicitly cautions against constant correlation across asset classes; it is shown only as a sensitivity target here. Diagonal shrinkage can also suppress real common risks. No optimal intensity is estimated. Sample covariance is noisy and bootstrap intervals omit unseen regimes."}
