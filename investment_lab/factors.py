"""Proxy-factor exposures and uncertainty; no fitted-alpha performance claim."""
import numpy as np
from .analytics import sample, nw_ols, result


def run():
    m,d,p,r,w=sample(); idx={s:i for i,s in enumerate(m.symbols)}
    x=np.column_stack([r[:,idx['VT']],r[:,idx['IEF']]-r[:,idx['SHY']],r[:,idx['GLD']]])
    labels=['Intercept (daily)','Global equity proxy','Treasury duration spread','Gold proxy']; rows=[]; windows=[]
    masks=[('Pre-inception',np.array([a<='2024-09-27' for a in d[1:]])),('Last 252 common sessions',np.arange(len(r))>=len(r)-252)]
    for name,mask in masks:
        beta,se,r2,resid=nw_ols((r@w)[mask],x[mask],5)
        corr=np.corrcoef(x[mask],rowvar=False); eigen=np.linalg.eigvalsh(corr)[::-1]
        windows.append({'window':name,'observations':int(mask.sum()),'r_squared':r2,'residual_annual_vol':float(resid.std(ddof=1)*np.sqrt(252)),'standardised_condition_number':float(np.linalg.cond(corr)),'first_pc_variance_share':float(eigen[0]/eigen.sum())})
        for label,b,s in zip(labels,beta,se):rows.append({'window':name,'factor':label,'loading':float(b),'hac_se':float(s),'approx_lower95':float(b-1.96*s),'approx_upper95':float(b+1.96*s)})
    last=[a for a in rows if a['window']==masks[-1][0] and not a['factor'].startswith('Intercept')]
    return result(f"Three tradable proxies explain {windows[-1]['r_squared']:.1%} of the fixed-weight basket's daily variation over the last 252 common sessions. Explanatory fit is not causality or alpha.",
        {'factor_loadings':rows,'diagnostics':windows},
        {'kind':'bar','labels':[a['factor'] for a in last],'values':[a['loading'] for a in last],'errors':[1.96*a['hac_se'] for a in last],'ylabel':'OLS loading · approximate HAC 95% interval','title':'Current-weight basket · proxy exposures and estimation uncertainty'},
        ['Current weights: 25 September 2026. Empirical sample ends 18 September 2026.','EUR adjusted returns; VT, IEF minus SHY, and GLD. Intercept is a daily statistical residual, not risk-free-adjusted alpha.','OLS includes intercept; Bartlett HAC covariance uses five lags. PCA describes the three standardised proxy factors.'],
        'Factors contain assets already in the basket, making some fit mechanical. Correlated proxies, omitted factors and asynchronous closes complicate interpretation. HAC intervals are approximate and not multiple-testing adjusted. These are not Fama–French factors, a macro causal model, or a forward return forecast.')
