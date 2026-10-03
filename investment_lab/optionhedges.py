"""European option mechanics, not an executable hedge recommendation."""
import math
import numpy as np
from .analytics import result


def price(spot, strike, years, rate, sigma, kind='put'):
    if min(spot,strike,years,sigma)<=0: raise ValueError('Positive pricing inputs required')
    if kind not in ['put','call']: raise ValueError('Unknown option type')
    cdf=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
    d1=(math.log(spot/strike)+(rate+.5*sigma*sigma)*years)/(sigma*math.sqrt(years))
    d2=d1-sigma*math.sqrt(years)
    call=spot*cdf(d1)-strike*math.exp(-rate*years)*cdf(d2)
    return call if kind=='call' else call-spot+strike*math.exp(-rate*years)


def payoff(terminal, put_premium, call_premium, policy, spot=100., rate=.03, years=.25, fee=.10):
    """P&L divided by original underlying notional; premiums funded from cash."""
    pnl=terminal-spot
    if policy in ['protective_put','collar']:
        pnl+=max(90-terminal,0)-(put_premium+fee)*math.exp(rate*years)
    if policy=='collar':
        pnl-=max(terminal-110,0)-(call_premium-fee)*math.exp(rate*years)
    return pnl/spot


def run():
    rows=[]; premiums=[]; policies=['unhedged','protective_put','collar']
    for sigma in [.15,.25,.40]:
        put=price(100,90,.25,.03,sigma); call=price(100,110,.25,.03,sigma,'call')
        premiums.append({'assumed_volatility':sigma,'put_premium_per_100':put,'call_premium_per_100':call,
                         'put_floor_pnl_per_notional':payoff(0,put,call,'protective_put'),
                         'collar_floor_pnl_per_notional':payoff(0,put,call,'collar'),
                         'collar_cap_pnl_per_notional':payoff(200,put,call,'collar')})
    put=price(100,90,.25,.03,.25);call=price(100,110,.25,.03,.25,'call')
    for terminal in np.linspace(50,140,19):
        rows.append({'terminal_spot':float(terminal),**{p:payoff(float(terminal),put,call,p) for p in policies}})
    return result(f'At 25% assumed volatility, the 90-strike put costs {put:.2f} per 100 of underlying. The collar exchanges upside above 110 for call premium; neither structure is costless.',
        {'volatility_sensitivity':premiums,'expiry_payoffs':rows},
        {'kind':'lines','x':[a['terminal_spot'] for a in rows],'series':[{'label':p.replace('_',' '),'values':[100*a[p] for a in rows]} for p in policies],
         'xlabel':'Underlying price at expiry (initial 100)','ylabel':'P&L / initial underlying notional (%)','title':'Three-month hedge mechanics · European options; cash opportunity cost included'},
        ['Synthetic underlying 100; European put strike 90 and call strike 110; maturity 0.25 years; continuous rate 3%; dividend yield zero.',
         'Black–Scholes volatility assumptions 15%, 25%, 40%; no live option quotes. Each option leg costs 0.10 per 100 notional.',
         'Premiums and fees are accrued at the assumed cash rate. P&L is incremental to cash opportunity cost, per underlying notional, not return on premium or margin.'],
        'No options are held in the portfolio. Constant volatility and European exercise ignore smile, skew, jumps and early assignment. A real ETF hedge requires dividends, multipliers, expiry, liquidity, cash and tax records; an index proxy introduces basis risk. Expiry floors do not describe interim mark-to-market or liquidation risk.')
