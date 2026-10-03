"""Monthly de-risking rule with past-only volatility and a no-leverage cap."""
from .analytics import sample, policy_simulation, costs_for, compact, result


def run():
    m,d,p,r,w=sample(); base=policy_simulation(d,p,m.weights,costs_for(m.symbols),'baseline')
    managed=policy_simulation(d,p,m.weights,costs_for(m.symbols),'volcontrol')
    grid=[]
    for target in [.08,.10,.12]:
        for mult in [0.,1.,2.]:
            a=policy_simulation(d,p,m.weights,costs_for(m.symbols,mult),'volcontrol',target_vol=target)
            grid.append({'target_vol':target,'cost_multiplier':mult,**compact(a)})
    return result(f"The 10% target rule realised {managed['annual_vol']:.1%} volatility and {managed['max_drawdown']:.1%} maximum drawdown versus {base['annual_vol']:.1%} and {base['max_drawdown']:.1%} for the monthly baseline. A target is not a risk guarantee.",
        {'policies':[compact(base),compact(managed)],'target_and_cost_sensitivity':grid,'signal_and_fill_dates':managed['trades'],'exposure_history':managed['history']},
        {'kind':'lines','x':[h['date'] for h in managed['history']],'series':[{'label':'Monthly baseline','values':[h['nav'] for h in base['history']]},{'label':'10% target, no leverage','values':[h['nav'] for h in managed['history']]}],'ylabel':'EUR NAV after fees','title':'Past-only 60-session volatility estimate · monthly execution'},
        ['Scale = clip(target / trailing 60-common-session basket volatility, 0.25, 1.00).','Targets 8%, 10%, 12% are all reported. Cash earns zero; no leverage, no forecast of expected return.','Signal/fill convention and costs are identical to the trend project; baseline uses the same monthly reset.'],
        'A monthly rule can react late to volatility spikes and miss rebounds after selling. The scaled basket is not the paper’s inverse-variance factor strategy. Lower risk can reflect simply holding more cash. No risk-matched alpha claim, cash interest, tax, liquidity feedback or intraday execution model.')
