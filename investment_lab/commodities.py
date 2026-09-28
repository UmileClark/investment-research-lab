"""Observed fund diversification and explicitly synthetic futures convergence."""
import numpy as np
from .data import Market


def convergence_return(spot, forward, collateral=.03, years=1/12, fee=.001):
    # A fully collateralised long contract converges to unchanged spot at expiry.
    # No instantaneous loss is assigned to buying a different contract at a roll.
    return (spot-forward)/forward + collateral*years-fee


def run():
    m=Market();syms=["VT","GLD","SLV","CPER","BNO"]
    windows=[]
    for name,archive,start,end in [("Pre-inception",m.pre,"2021-09-27","2024-09-27"),("Reconstruction",m.post,"2024-09-30","2026-09-18")]:
        dates,p=m.panel(archive,start,end,syms);r=p[1:]/p[:-1]-1
        corr=np.corrcoef(r.T)
        windows.append({"window":name,"start":dates[0],"end":dates[-1],"observations":len(r),
                        "rows":[{"ticker":s,"equity_correlation":float(corr[0,i]),"annualised_volatility":float(np.std(r[:,i],ddof=1)*np.sqrt(252))} for i,s in enumerate(syms)],
                        "correlation":corr.tolist()})
    curves=[]
    for name,forward in [("Backwardation",98),("Flat",100),("Contango",102)]:
        monthly=convergence_return(100,forward)
        curves.append({"curve":name,"spot":100,"one_month_future":forward,"spot_return":0,
                       "futures_convergence":(100-forward)/forward,"monthly_collateralised_return":monthly,
                       "hypothetical_12_month_return":(1+monthly)**12-1})
    return {"symbols":syms,"windows":windows,"curve_scenarios":curves,
            "limitation":"Fund returns include their particular structure and costs; no claim to replicate diversified commodity-futures academic indices. Synthetic curves reset identically each month with unchanged spot, 3% collateral and 10 bp monthly cost; these are not forecasts or actual CPER/BNO returns."}
