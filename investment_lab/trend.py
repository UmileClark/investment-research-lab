"""Long/cash time-series trend research, not a replication of futures TSMOM."""
from .analytics import sample, policy_simulation, costs_for, compact, result


def run():
    m,d,p,r,w=sample()
    baseline=policy_simulation(d,p,m.weights,costs_for(m.symbols),'baseline')
    base=policy_simulation(d,p,m.weights,costs_for(m.symbols),'trend')
    grid=[]
    for days in [126,189,252]:
        for multiplier in [0.,1.,2.]:
            a=policy_simulation(d,p,m.weights,costs_for(m.symbols,multiplier),'trend',lookback=days)
            grid.append({'lookback_sessions':days,'cost_multiplier':multiplier,**compact(a)})
    return result(f"The stated 252-session long/cash rule returned {base['total_return']:.1%} after costs versus {baseline['total_return']:.1%} for the same allocation reset monthly. All nine lookback/cost cases are disclosed; none is selected as optimal.",
        {'policies':[compact(baseline),compact(base)],'parameter_sensitivity':grid,'signal_and_fill_dates':base['trades'],'trend_history':base['history']},
        {'kind':'lines','x':[h['date'] for h in base['history']],'series':[{'label':'Monthly baseline','values':[h['nav'] for h in baseline['history']]},{'label':'252-session long/cash','values':[h['nav'] for h in base['history']]}],'ylabel':'EUR NAV after modelled fees','title':'Same inception allocation · monthly signals, later-close fills'},
        ['Start 30 September 2024; fixed inception universe and weights; monthly last-calendar-weekday review.','Positive trailing EUR adjusted return retains the initial asset budget; otherwise allocate it to zero-yield EUR cash. No shorts or leverage.','Execution at the next common close. 25 bp per side, 50 bp for crypto. Asset exposure earns subsequent returns only. Missing review-day quote skips the review.'],
        'Rules and assets were chosen in October 2026 with knowledge of the past; this is retrospective research despite chronological execution. Reversals and repeated crossings can cause whipsaw and tax costs. ETF long/cash rules differ from the paper’s diversified, volatility-scaled long/short futures. Common dates omit some markets’ sessions and crypto weekends.')
