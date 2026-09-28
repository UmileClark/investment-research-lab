"""Exact synthetic-bond repricing; illustrative ETF duration decision analysis."""
import numpy as np
from .data import Market
from .math import bond_greeks, bond_price


def curve_price(years, coupon, nodes, rates):
    times = np.arange(.5,years+.1,.5)
    cf = np.full(len(times),100*coupon/2)
    cf[-1] += 100
    spot = np.interp(times,nodes,rates)
    return float(np.sum(cf/(1+spot/2)**(2*times)))


def run():
    m = Market()
    weights = {h["ticker"]:h["weight"] for h in m.current["holdings"]}
    greeks = {"2y":bond_greeks(.04,.04,2),"8y":bond_greeks(.04,.04,8)}
    scenarios = []
    for bp in [-200,-100,-50,0,50,100,200]:
        dy = bp/10000
        g = greeks["8y"]
        exact = bond_price(.04,.04+dy,8)/g["price"]-1
        approx = -g["duration"]*dy+.5*g["convexity"]*dy*dy
        scenarios.append({"shock_bp":bp,"exact_return":exact,"duration_convexity_return":approx,"error_bp":(approx-exact)*10000})
    nodes = [1,2,5,10,30]
    base = np.full(5,.04)
    key = []
    for i,node in enumerate(nodes):
        up,down=base.copy(),base.copy()
        up[i]+=.0001;down[i]-=.0001
        key.append({"tenor":node,"duration_2y":(curve_price(2,.04,nodes,down)-curve_price(2,.04,nodes,up))/.02,
                    "duration_8y":(curve_price(8,.04,nodes,down)-curve_price(8,.04,nodes,up))/.02})
    # Explicit teaching assumptions, not current verified ETF analytics.
    d_ief,d_shy=7.2,1.8
    before=weights["IEF"]*d_ief+weights["SHY"]*d_shy
    after=before-.02*d_ief+.02*d_shy
    cost=.02*.0025*2
    shift=[]
    for bp in [-100,-50,0,50,100]:
        delta=(before-after)*bp/10000-cost
        shift.append({"parallel_shock_bp":bp,"incremental_nav_return_after_cost":delta,"incremental_eur":delta*m.current["nav"]})
    curves=[]
    for name,shock in [("parallel +100 bp",[.01]*5),("bear steepener",[.0025,.0025,.0075,.0125,.015]),("bull flattener",[-.0025,-.0025,-.0075,-.0125,-.015])]:
        curves.append({"scenario":name,"2y_return":curve_price(2,.04,nodes,base+shock)/100-1,"8y_return":curve_price(8,.04,nodes,base+shock)/100-1})
    return {"synthetic_bonds":greeks,"convexity_scenarios":scenarios,"key_rate_durations":key,"curve_scenarios":curves,
            "assumed_ief_duration":d_ief,"assumed_shy_duration":d_shy,"portfolio_duration_before":before,"portfolio_duration_after":after,
            "portfolio_duration_change":after-before,"shift_cost_eur":cost*m.current["nav"],
            "parallel_yield_rise_break_even_bp":cost/(before-after)*10000,"pending_shift_scenarios":shift,
            "limitation":"Instantaneous USD price shocks only: no coupon carry, roll-down, tax, FX or ETF reconstitution. All yields and ETF durations are illustrative. Pending shift remains unfilled."}
