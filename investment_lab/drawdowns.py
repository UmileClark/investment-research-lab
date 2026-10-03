"""Depth, time under water and block-resampling uncertainty."""
import math
import numpy as np
from .data import read
from .analytics import sample, result


def episodes(dates, values):
    values=np.asarray(values,float); peak=0; trough=0; active=False; out=[]
    for i in range(1,len(values)):
        if values[i]>=values[peak]:
            if active:
                out.append({'peak_date':dates[peak],'trough_date':dates[trough],'recovery_date':dates[i],
                            'depth':float(values[trough]/values[peak]-1),'underwater_sessions':i-peak,'recovered':True})
            peak=i;trough=i;active=False
        else:
            active=True
            if values[i]<values[trough]:trough=i
    if active:out.append({'peak_date':dates[peak],'trough_date':dates[trough],'recovery_date':None,
                          'depth':float(values[trough]/values[peak]-1),'underwater_sessions':len(values)-1-peak,'recovered':False})
    return sorted(out,key=lambda a:a['depth'])


def bootstrap_drawdowns(r, block, runs=600, horizon=252, seed=20261003):
    rng=np.random.default_rng(seed); outcomes=[]
    for _ in range(runs):
        starts=rng.integers(0,len(r),math.ceil(horizon/block))
        ix=((starts[:,None]+np.arange(block))%len(r)).ravel()[:horizon]
        wealth=np.r_[1.,np.cumprod(1+r[ix])]
        outcomes.append(float((wealth/np.maximum.accumulate(wealth)-1).min()))
    return np.asarray(outcomes)


def run():
    h=read('historical_book.json')['history']; dates=['2024-09-27']+[x['date'] for x in h]; nav=[100000.]+[x['nav'] for x in h]
    actual=episodes(dates,nav); m,d,p,r,w=sample(); basket=r@w; rows=[]
    for block in [1,5,20]:
        draws=bootstrap_drawdowns(basket,block)
        rows.append({'block_sessions':block,'runs':len(draws),'horizon_sessions':252,'p05_max_drawdown':float(np.quantile(draws,.05)),'median_max_drawdown':float(np.median(draws)),'p95_max_drawdown':float(np.quantile(draws,.95)),'fraction_below_minus20':float(np.mean(draws<-.2))})
    dd=np.asarray(nav)/np.maximum.accumulate(nav)-1
    worst=actual[0]
    return result(f"The reconstructed ledger’s deepest drawdown was {worst['depth']:.1%}. Its episode lasted {worst['underwater_sessions']} recorded sessions; recovery status and dates are retained. Resampling current weights is a separate risk experiment.",
        {'historical_episodes':actual,'bootstrap_sensitivity':rows},
        {'kind':'lines','x':dates,'series':[{'label':'Reconstructed ledger drawdown','values':(100*dd).tolist()}],'ylabel':'Drawdown from prior peak (%)','title':'Historical ledger · depth and recovery are separate dimensions'},
        ['Ledger starts with EUR 100,000 before initial fees; episode recovery requires matching or exceeding the prior peak.','Bootstrap uses current weights applied to the 2021–2026 archive, zero cash return and hypothetical daily constant weights.','600 circular block samples at lengths 1, 5 and 20; 252-session paths. The 5th percentile is the more adverse tail.'],
        'Observed drawdown is not a maximum possible loss. Resampling reuses a short sample and cannot invent unseen crises; frequencies are conditional simulation results, not calibrated future probabilities. Current-weight simulation and the historical discretionary ledger are different portfolios. No drawdown optimisation or replication of the cited paper.')
