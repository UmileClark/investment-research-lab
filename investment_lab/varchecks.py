"""Historical and EWMA-normal VaR coverage, forecasts use only earlier returns."""
import math
from statistics import NormalDist
import numpy as np
from .analytics import sample, result


def kupiec(exceptions, observations, tail):
    if not 0<tail<1 or observations<=0 or not 0<=exceptions<=observations:raise ValueError('Invalid coverage inputs')
    p=exceptions/observations
    def term(n,q):return 0. if n==0 else n*math.log(q)
    lr=max(0.,2*(term(exceptions,p)+term(observations-exceptions,1-p)-term(exceptions,tail)-term(observations-exceptions,1-tail)))
    return lr,math.erfc(math.sqrt(lr/2))


def forecasts(r, window=250, decay=.94):
    out=[]; variance=float(np.mean(np.asarray(r[:60])**2))
    for i,value in enumerate(r):
        if i>=window:
            prior=r[i-window:i]
            row={'index':i,'realised_loss':float(-value)}
            for tail in [.05,.01]:
                key=str(int(tail*100)); z=NormalDist().inv_cdf(1-tail)
                row['historical_var'+key]=float(np.quantile(-prior,1-tail))
                row['ewma_var'+key]=float(z*math.sqrt(variance))
            out.append(row)
        # Update after recording the forecast for this return.
        variance=decay*variance+(1-decay)*value**2
    return out


def run():
    m,d,p,r,w=sample(); basket=r@w; all_rows=forecasts(basket)
    obs=[{'date':d[a['index']+1],**a} for a in all_rows if d[a['index']+1]>='2024-09-30']; coverage=[]
    for model in ['historical','ewma']:
        for tail in [.05,.01]:
            field=model+'_var'+str(int(tail*100)); flags=np.array([a['realised_loss']>a[field] for a in obs])
            n=len(flags);x=int(flags.sum());lr,pv=kupiec(x,n,tail)
            adjacent=int(np.sum(flags[1:]&flags[:-1]));ph=x/n;z=1.96
            center=(ph+z*z/(2*n))/(1+z*z/n);radius=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/(1+z*z/n)
            coverage.append({'model':model,'tail_probability':tail,'observations':n,'exceptions':x,'expected_exceptions':n*tail,'exception_rate':ph,'wilson_lower95':center-radius,'wilson_upper95':center+radius,'kupiec_lr':lr,'asymptotic_p_value':pv,'adjacent_breach_pairs':adjacent})
    a=next(x for x in coverage if x['model']=='historical' and x['tail_probability']==.01)
    return result(f"Rolling historical 99% VaR recorded {a['exceptions']} breaches in {a['observations']} evaluation sessions (expected {a['expected_exceptions']:.1f}). Coverage and clustering must be examined together.",
        {'coverage':coverage,'daily_forecasts':obs},
        {'kind':'lines','x':[a['date'] for a in obs],'series':[{'label':'Realised loss','values':[100*a['realised_loss'] for a in obs]},{'label':'Historical 99% VaR','values':[100*a['historical_var1'] for a in obs]},{'label':'EWMA-normal 99% VaR','values':[100*a['ewma_var1'] for a in obs]}],'ylabel':'Daily loss / VaR (% of NAV)','title':'Prior-only forecasts · retrospective constant-weight basket'},
        ['Current frozen weights applied to common-session EUR returns; this is hypothetical P&L, not actual ledger P&L.','Historical window 250; EWMA lambda 0.94, zero conditional mean, normal quantile. Seed uses the first 60 returns; scoring starts after 250.','Kupiec unconditional-coverage LR uses an asymptotic chi-square(1) reference; Wilson intervals show count uncertainty. Adjacent pairs are descriptive only.'],
        'Neither model certifies tail protection. Small breach counts make asymptotic p-values fragile; no conditional-independence test or regulatory approval is claimed. Model selection is retrospective, observations are dependent and realised P&L is constructed with later weights. Do not use a passed coverage check as proof of a sound expected-shortfall model.')
