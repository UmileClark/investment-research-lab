"""Cash-funded crypto sizing and explicitly stressed co-movement."""
from datetime import date, timedelta
import numpy as np
from .analytics import sample, stats, result
from .math import risk_contributions


def run():
    m,d,p,r,w=sample(); indices=[m.symbols.index(s) for s in ['BTC-USD','ETH-USD']]
    current=float(w[indices].sum()); ratio=w[indices]/current if current else np.array([2/3,1/3])
    base=w.copy();base[indices]=0.;cov=np.cov(r,rowvar=False)*252
    vol=np.sqrt(np.diag(cov));corr=cov/np.outer(vol,vol)
    # Convex mixture with a rank-one all-positive correlation target stays PSD.
    stressed_cov=np.outer(vol,vol)*(.5*corr+.5*np.ones_like(corr))
    rows=[]
    for allocation in sorted(set([0.,.01,.02,.03,.05,current])):
        a=base.copy();a[indices]=ratio*allocation
        if a.sum()>1:raise ValueError('Crypto budget exceeds available cash')
        sigma,contrib=risk_contributions(a,cov); stressed,_=risk_contributions(a,stressed_cov)
        rows.append({'crypto_weight':allocation,'btc_weight':float(a[indices[0]]),'eth_weight':float(a[indices[1]]),'cash_weight':float(1-a.sum()),'annual_vol':sigma,'crypto_variance_share':float(contrib[indices].sum()),'stressed_annual_vol':stressed,**{k:v for k,v in stats(r@a).items() if k!='annual_vol'}})
    weekends=[]
    for symbol in ['BTC-USD','ETH-USD']:
        series=m.combined[symbol]['rows'];lookup={x['date']:x for x in series}
        gaps=[]
        for a in series:
            friday=date.fromisoformat(a['date'])
            b=lookup.get((friday+timedelta(days=2)).isoformat())
            if friday.weekday()==4 and b:
                gaps.append(b['close']/a['close']-1)
        # The frozen common-calendar archive may exclude weekends entirely.
        weekends.append({'ticker':symbol,'friday_to_sunday_observations':len(gaps),'worst_spot_gap':float(min(gaps)) if gaps else None,'coverage':'Observed USD spot only' if gaps else 'No Friday-to-Sunday pairs; weekend risk unmeasured'})
    live=next(a for a in rows if a['crypto_weight']==current)
    return result(f"The frozen {current:.1%} crypto capital allocation contributes {live['crypto_variance_share']:.1%} of sample portfolio variance. Cash-funded alternatives are compared without selecting the best historical return.",
        {'allocation_grid':rows,'weekend_coverage':weekends},
        {'kind':'lines','x':[100*a['crypto_weight'] for a in rows],'series':[{'label':'Sample covariance','values':[100*a['annual_vol'] for a in rows]},{'label':'Higher-correlation stress','values':[100*a['stressed_annual_vol'] for a in rows]}],'xlabel':'Crypto capital weight (%)','ylabel':'Annualised portfolio volatility (%)','title':'BTC/ETH in current proportions · allocation funded from EUR cash'},
        ['Other current weights held fixed; changes to crypto are financed from zero-return cash.','Stress correlation = 50% sample + 50% all-ones matrix; historical marginal volatilities unchanged. This is an assumed co-movement shock.','Common-session risk estimates exclude most crypto weekend moves. Separate coverage audit reports whether weekend pairs exist.'],
        'Historical covariance can understate simultaneous deleveraging, exchange failure and weekend gaps. A USD spot proxy omits custody, funding, exchange, staking and slippage risks. Higher correlation alone is not a full crisis scenario. Historical constant-weight performance is not a proposed trade or evidence that a crypto weight is optimal.')
