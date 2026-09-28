"""One entry point builds JSON, CSV, figures and short decision-focused reports."""
from pathlib import Path
from datetime import date
import csv
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .data import ROOT, verify_inputs, read
from .catalog import PROJECTS, SOURCES
from . import accounting, risk, rates, fx, valuation, rebalancing, commodities, events

FUNCTIONS={"audit":accounting.audit,"attribution":accounting.attribution,"risk":risk.run,"rates":rates.run,
           "fx":fx.run,"valuation":valuation.run,"rebalancing":rebalancing.run,"commodities":commodities.run,"events":events.run}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                     "axes.labelcolor":"#10263c","text.color":"#10263c","axes.titleweight":"bold","figure.facecolor":"white",
                     "svg.hashsalt":"fabio-research-20260928"})
NAVY,TEAL,RED,GOLD="#163b5c","#158579","#b44b47","#bc9038"


def serial(value):
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,np.ndarray):return value.tolist()
    raise TypeError(type(value).__name__)


def summary(pid,r):
    if pid=="audit":return f"All {r['daily_marks']} historical NAV marks reconcile. Replayed NAV: €{r['historical_nav']:,.2f}; current marks: €{r['current_nav']:,.2f}. Pending order excluded."
    if pid=="risk":return f"Current weights on the pre-inception sample imply {r['annualised_volatility']:.2%} annual volatility; daily 97.5% ES is {r['daily_es975']:.2%}. The block-bootstrap volatility range is {r['sample_vol_bootstrap95'][0]:.2%}–{r['sample_vol_bootstrap95'][2]:.2%}."
    if pid=="attribution":return f"18–25 September: €{r['totals']['local_price_eur']:,.2f} local-price P&L plus €{r['totals']['fx_eur']:,.2f} currency P&L equals €{r['totals']['total_eur']:,.2f}."
    if pid=="rates":return f"The pending 2% shift reduces assumed portfolio duration by {-r['portfolio_duration_change']:.3f} years. Two-leg costs are €{r['shift_cost_eur']:.2f}; a parallel yield rise of {r['parallel_yield_rise_break_even_bp']:.1f} bp covers them in the instantaneous approximation."
    if pid=="fx":return f"Illustrative quarterly carry is erased by spot losses of {-r['pairs'][0]['break_even_spot_return']:.2%} for AUD/JPY and {-r['pairs'][1]['break_even_spot_return']:.2%} for MXN/JPY. Neither is a funded portfolio trade."
    if pid=="valuation":return f"The September-2024 CME price requires {r['implied_five_year_cash_growth']:.2%} annual cash growth under the stated discount assumptions. Base proxy value: ${r['base_value']:.2f}; {r['terminal_value_share']:.1%} comes from the terminal value."
    if pid=="rebalancing":return "; ".join(f"{x['rule'].replace('_',' ').capitalize()}: {x['total_return']:.2%} net, €{x['fees']:.0f} fees" for x in r["results"])+". These are historical comparisons, not verified alpha."
    if pid=="commodities":return f"With unchanged spot and an identically resetting 2% contango curve, the illustrative collateralised futures return is {r['curve_scenarios'][2]['hypothetical_12_month_return']:.2%} over twelve months. This is a mechanics example, not a forecast."
    if pid=="events":return "; ".join(f"{e['ticker']} {e['event_date']}: {e['event_day_abnormal_return']:.2%} event-day abnormal return" for e in r["events"])+". Selected events do not establish causality."


def tables(pid,r):
    if pid=="audit":return {"reconciliation":[{"measure":k,"value":v} for k,v in r.items() if isinstance(v,(float,int,bool))]}
    if pid=="risk":return {"risk_contributions":r["rows"],"covariance_sensitivity":r["sensitivity"]}
    if pid=="attribution":return {"price_fx":r["rows"]}
    if pid=="rates":return {"duration_convexity":r["convexity_scenarios"],"key_rate_duration":r["key_rate_durations"],"curve_shocks":r["curve_scenarios"],"pending_shift":r["pending_shift_scenarios"]}
    if pid=="fx":return {"carry_pairs":r["pairs"],"carry_scenarios":r["scenarios"]}
    if pid=="valuation":return {"dcf_scenarios":r["scenarios"],"valuation_grid":r["grid"]}
    if pid=="rebalancing":return {"rule_results":[{k:v for k,v in a.items() if k not in ["history","trades"]} for a in r["results"]],"cost_sensitivity":r["cost_sensitivity"],
                                    **{x["rule"]+"_history":x["history"] for x in r["results"]},
                                    **{x["rule"]+"_trades":[{k:v for k,v in t.items() if k!="amounts"} for t in x["trades"]] for x in r["results"]}}
    if pid=="commodities":return {"commodity_correlations":[{"window":w["window"],**a} for w in r["windows"] for a in w["rows"]],"synthetic_curves":r["curve_scenarios"]}
    if pid=="events":return {"event_summary":[{k:e[k] for k in ["ticker","event_date","benchmark","alpha_daily","beta","estimation_start","estimation_end","car_minus5_plus5","event_day_abnormal_return"]} for e in r["events"]],
                             **{e["ticker"]+"_"+e["event_date"]:e["rows"] for e in r["events"]}}


def chart(pid,r,out):
    fig,ax=plt.subplots(figsize=(10,5.4),layout="constrained")
    if pid=="audit":
        h=read("historical_book.json")["history"]
        ax.plot([date.fromisoformat(x["date"]) for x in h],[x["nav"] for x in h],color=NAVY)
        ax.set(ylabel="EUR NAV",title="Replayed historical NAV · 515 reconciled marks")
    elif pid=="risk":
        rows=sorted(r["rows"],key=lambda x:x["risk_share"],reverse=True)[:10];x=np.arange(len(rows))
        ax.bar(x-.18,[a["weight"]*100 for a in rows],.36,label="Capital weight",color=NAVY)
        ax.bar(x+.18,[a["risk_share"]*100 for a in rows],.36,label="Share of variance",color=TEAL)
        ax.set_xticks(x,[a["ticker"] for a in rows],rotation=30)
        ax.set(ylabel="%",title="Current capital weights and historical risk shares");ax.legend()
    elif pid=="attribution":
        rows=sorted([a for a in r["rows"] if abs(a["total_eur"])>.001],key=lambda a:a["total_eur"])
        y=np.arange(len(rows));ax.barh(y-.18,[a["local_price_eur"] for a in rows],.36,label="Local price",color=NAVY)
        ax.barh(y+.18,[a["fx_eur"] for a in rows],.36,label="FX (including interaction)",color=TEAL)
        ax.set_yticks(y,[a["ticker"] for a in rows]);ax.axvline(0,color="#999",lw=.7)
        ax.set(xlabel="EUR P&L",title="18–25 September 2026 · fixed-share attribution");ax.legend()
    elif pid=="rates":
        rows=r["pending_shift_scenarios"]
        ax.bar([str(a["parallel_shock_bp"]) for a in rows],[a["incremental_eur"] for a in rows],color=[RED if a["incremental_eur"]<0 else TEAL for a in rows])
        ax.axhline(0,color="#999",lw=.7);ax.set(xlabel="Parallel yield shock (bp)",ylabel="Incremental EUR P&L after fees",title="Pending 2% IEF → SHY shift · illustrative durations")
    elif pid=="fx":
        for pair,color in [("AUDJPY",NAVY),("MXNJPY",TEAL)]:
            a=[s for s in r["scenarios"] if s["pair"]==pair];ax.plot([s["spot_return"]*100 for s in a],[s["pnl_per_borrowed_notional"]*100 for s in a],marker="o",label=pair,color=color)
        ax.axhline(0,color="#999",lw=.7);ax.set(xlabel="Target currency move against JPY (%)",ylabel="P&L / borrowed JPY notional (%)",title="Three-month carry · historical rate anchors, 10 bp cost");ax.legend()
    elif pid=="valuation":
        grid=np.array([a["value"] for a in r["grid"]]).reshape(5,5)
        im=ax.imshow(grid,cmap="Blues",aspect="auto")
        for (i,j),v in np.ndenumerate(grid):ax.text(j,i,f"${v:.0f}",ha="center",va="center",color="white" if v>230 else NAVY)
        ax.set_xticks(range(5),["7%","8%","9%","10%","11%"]);ax.set_yticks(range(5),["2%","5%","8%","11%","14%"])
        ax.set(xlabel="Cost of equity",ylabel="Five-year cash growth",title="CME cash-proxy value · 3% terminal growth; Sep-2024 reference $218.30")
    elif pid=="rebalancing":
        for a,color in zip(r["results"],[NAVY,TEAL,GOLD]):
            ax.plot([date.fromisoformat(h["date"]) for h in a["history"]],[h["nav"] for h in a["history"]],color=color,label=a["rule"].replace("_"," "))
        ax.set(ylabel="EUR NAV after modelled fees",title="Same initial allocation · three rebalancing policies");ax.legend()
    elif pid=="commodities":
        x=np.arange(4)
        for w,offset,color in zip(r["windows"],[-.18,.18],[NAVY,TEAL]):
            ax.bar(x+offset,[a["equity_correlation"] for a in w["rows"]][1:],.36,label=w["window"],color=color)
        ax.set_xticks(x,r["symbols"][1:]);ax.axhline(0,color="#999",lw=.7)
        ax.set(ylabel="Correlation with VT · EUR daily returns",title="Commodity fund correlations are window-dependent");ax.legend()
    elif pid=="events":
        for e,color in zip(r["events"],[NAVY,TEAL,GOLD]):
            ax.plot([a["day"] for a in e["rows"]],[a["cumulative_abnormal_return"]*100 for a in e["rows"]],marker="o",color=color,label=e["ticker"]+" "+e["event_date"])
        ax.axvline(0,color="#999",lw=.7,ls="--");ax.axhline(0,color="#999",lw=.7)
        ax.set(xlabel="Common-market sessions from release",ylabel="Arithmetic CAR (%)",title="Selected release windows · descriptive, not causal");ax.legend(fontsize=9)
    ax.grid(axis="y",alpha=.15)
    fig.savefig(out/f"{pid}.png",dpi=170)
    fig.savefig(out/f"{pid}.svg",metadata={"Date":None})
    plt.close(fig)


def report(pid,result,out):
    project=next(p for p in PROJECTS if p["id"]==pid)
    text=f"# {project['title']}\n\nResearch authored 28 September 2026 · {project['status']}\n\n## Question\n\n{project['question']}\n\n## Computed finding\n\n{summary(pid,result)}\n\n![Model output]({pid}.png)\n\n"
    for key,title in [("method","Method"),("decision","Investment implication"),("falsifier","What could invalidate the interpretation"),("next","Next research step"),("interview","Discussion prompt")]:
        text+=f"## {title}\n\n{project[key]}\n\n"
    text+=f"## Limitations\n\n{result['limitation']}\n\n## Reproduce\n\n```bash\npython -m investment_lab {pid}\n```\n\nFull numerical output: [{pid}.json]({pid}.json). CSV tables use decimal returns, not percentages.\n\n## Sources and use\n\n"
    sources={**SOURCES,**{s[0]:{"title":s[1],"url":s[3],"application":"Primary dated release for the historical event."} for s in read("book.json")["sources"] if s[0] not in SOURCES}}
    for sid in project["sources"]:
        s=sources[sid];text+=f"- [{s['title']}]({s['url']}): {s['application']}\n"
    (out/f"{pid}.md").write_text(text)


def run_project(pid, output=None):
    verify_inputs()
    out=Path(output) if output else ROOT/"reports"
    out.mkdir(parents=True,exist_ok=True)
    result=FUNCTIONS[pid]()
    (out/f"{pid}.json").write_text(json.dumps(result,indent=2,default=serial,allow_nan=False))
    for name,rows in tables(pid,result).items():
        if not rows:continue
        with (out/f"{pid}_{name}.csv").open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    chart(pid,result,out);report(pid,result,out)
    return result


def run_all(output=None):
    results={p["id"]:run_project(p["id"],output) for p in PROJECTS}
    out=Path(output) if output else ROOT/"reports"
    manifest={"authored":"2026-09-28","portfolio_marks":"2026-09-25","projects":[{**p,"finding":summary(p["id"],results[p["id"]])} for p in PROJECTS],"sources":SOURCES,
              "disclosure":"Built with AI assistance in September 2026. The earlier portfolio is a retrospective reconstruction; these projects were not tools used live in 2024. No demonstrated predictive alpha or real-money track record is claimed."}
    (out/"catalog.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return results
