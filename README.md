# Fabio's Investment Research Lab

Nineteen reproducible Python projects supporting a multi-asset paper portfolio. The objective is to make investment decisions inspectable: their data, assumptions, alternatives, accounting and failure conditions.

**[Open the public portfolio and research projects](https://fabio-investment-lab.fraccafabio.chatgpt.site/#projects)**

Research authored **28 September and 3 October 2026**. Portfolio inception is a **retrospective reconstruction** beginning 30 September 2024, with an information cutoff of 27 September 2024. Current published marks are 25 September 2026. These tools were built in 2026, with AI assistance; they are not presented as tools used live in 2024. This is a research portfolio, not a real-money track record or a claim of predictive alpha.

**[GitHub repository](https://github.com/UmileClark/investment-research-lab)**

## Start here

1. Read [the research process](docs/RESEARCH_PROCESS.md) and [the interview guide](docs/INTERVIEW_GUIDE.md).
2. Run the accounting audit, then the project closest to your investment question.
3. Read both the computed finding and the limitations. A result can challenge a thesis.

| Project | Question | Report | Implementation |
|---|---|---|---|
| Accounting | Does every euro reconcile? | [Audit](reports/audit.md) | [accounting.py](investment_lab/accounting.py) |
| Portfolio risk | Which holdings consume risk? | [Risk](reports/risk.md) | [risk.py](investment_lab/risk.py) |
| Price / FX attribution | What drove the forward gain? | [Attribution](reports/attribution.md) | [accounting.py](investment_lab/accounting.py) |
| Rates | What does shortening duration change? | [Rates](reports/rates.md) | [rates.py](investment_lab/rates.py) |
| FX carry | How easily can spot losses erase carry? | [FX](reports/fx.md) | [fx.py](investment_lab/fx.py) |
| CME valuation | What growth did the 2024 price require? | [Valuation](reports/valuation.md) | [valuation.py](investment_lab/valuation.py) |
| Rebalancing | Does more trading help? | [Rules](reports/rebalancing.md) | [rebalancing.py](investment_lab/rebalancing.py) |
| Commodities | What is spot risk versus futures exposure? | [Commodities](reports/commodities.md) | [commodities.py](investment_lab/commodities.py) |
| Event studies | How unusual were Novo/Rheinmetall moves? | [Events](reports/events.md) | [events.py](investment_lab/events.py) |
| Cross-asset stress laboratory | What breaks when rates, equities, crypto and currencies move together? | [stress](reports/stress.md) | [stress.py](investment_lab/stress.py) |
| EUR currency hedge frontier | How sensitive is portfolio risk to partial currency hedging and its cost? | [currency](reports/currency.md) | [currency.py](investment_lab/currency.py) |
| Factor exposure and model fragility | How much of the basket is explained by equity, duration and gold proxies? | [factors](reports/factors.md) | [factors.py](investment_lab/factors.py) |
| Trend rule with delayed execution | Does a transparent long/cash trend rule change the portfolio’s loss profile? | [trend](reports/trend.md) | [trend.py](investment_lab/trend.py) |
| Cash-funded volatility targeting | What does reducing exposure after volatility rises cost and protect? | [volcontrol](reports/volcontrol.md) | [volcontrol.py](investment_lab/volcontrol.py) |
| Drawdown and recovery anatomy | How deep and how long were losses, and how path-dependent is that result? | [drawdowns](reports/drawdowns.md) | [drawdowns.py](investment_lab/drawdowns.py) |
| VaR forecast coverage checks | Do simple daily loss forecasts produce the expected number of breaches? | [varchecks](reports/varchecks.md) | [varchecks.py](investment_lab/varchecks.py) |
| Crypto allocation and correlation stress | How much risk can a small Bitcoin/Ether allocation consume? | [crypto-budget](reports/crypto-budget.md) | [crypto_budget.py](investment_lab/crypto_budget.py) |
| Protective puts and collar economics | What is the actual trade-off between downside protection, premium and foregone upside? | [option-hedges](reports/option-hedges.md) | [optionhedges.py](investment_lab/optionhedges.py) |
| Prospective thesis and probability register | How can future investment judgements become auditable evidence? | [decision-log](reports/decision-log.md) | [decisionlog.py](investment_lab/decisionlog.py) |

See [the ten-project release](docs/RELEASE_2026_10_03.md), [weekly review process](docs/WEEKLY_REVIEW_IT.md) and [prospective register guide](docs/DECISION_REGISTER.md).

## Run locally

Python 3.11+; validated with Python 3.12.14, NumPy 2.3.5 and Matplotlib 3.10.8. Run from this repository's root; the code reads adjacent frozen `data/` files. No API key, broker connection or network access is required after dependencies are installed.

```bash
git clone https://github.com/UmileClark/investment-research-lab.git
cd investment-research-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m investment_lab all
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`. If activation is restricted, run `.venv\Scripts\python.exe` directly. A single project can be run with `python -m investment_lab risk` or any ID in the table. Use `--output /path/to/results` to keep a separate experiment.

Open `Fabio_Investment_Lab.code-workspace` in VS Code. Select the `.venv` Python interpreter. Included build/test tasks and the debugger run the projects. Nineteen notebooks in `notebooks/` are optional; installing the recommended Jupyter extension and `ipykernel` enables interactive execution. The committed notebook outputs are generated by `python scripts/execute_notebooks.py`, which executes this project's simple code cells using standard Python.

## Outputs and checks

Each project writes JSON, CSV tables, a PNG, an SVG and a Markdown report to `reports/`. CSV rates and weights are decimals: 0.10 means 10%. `python scripts/export_excel_inputs.py` writes read-only CSV snapshots for Excel to `reports/excel/`. This export does not overwrite the public portfolio or import trades.

The tests cover NAV reconciliation, fees, stale/future quotes, adjusted-price bridging, no rewriting of earlier decisions when future prices change, bond pricing, forward parity, DCF inversion and risk identities. The GitHub Actions workflow reproduces the project on push. Check the Actions tab for the status of each run; a local pass is separate from CI.

## Data and model boundaries

- All source snapshots and their retrieval metadata are in `data/`; `data/manifest.json` contains SHA-256 hashes. The programs fail if frozen inputs change.
- Historical prices were downloaded in 2026 and are not point-in-time vendor vintages. Calendar cutoffs alone do not remove hindsight or vendor revisions.
- The historical ledger uses adjusted-return index units, then converts to unadjusted share equivalents at handover. The forward attribution uses fixed shares and verified absence of intervening corporate actions.
- The risk project shows covariance sensitivity. Constant correlation across asset classes is explicitly cautioned against in the source paper; it is not treated as a validated multi-asset optimiser.
- Rates and carry assumptions are labelled. There is no invented historical FX carry profit. No future pending fill is booked.
- AI assistance is disclosed. The owner should rerun, modify and defend each model before describing it as a skill in an interview.

See [sources](docs/SOURCES.md), [data provenance](docs/DATA_DICTIONARY.md), [development priorities](docs/ROADMAP.md) and [GitHub / VS Code setup](docs/SETUP_IT.md). Third-party market data and publications retain their own rights; no licence to those materials is granted by this repository. The project links to papers instead of redistributing their full text.
