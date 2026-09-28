# Discuss the research, not just the return

Suggested opening: “I built an AI-assisted research framework around a multi-asset paper portfolio. I distinguish the reconstructed historical study from prospective decisions. I can reproduce the accounting and explain where the models are useful, where they are fragile, and where the results challenge my original thesis.” Adapt this only after you can run and explain the code yourself.

## Three cases worth preparing in depth

**CME: business quality versus price.** Explain the revenue drivers and why volatility is not a sufficient earnings forecast. Derive the cash proxy from the annual report, change the growth and discount assumptions, and explain the terminal-value concentration. The 2024 reference price requires more growth than the base case assumes. That is a challenge to the thesis, not an inconvenience to conceal.

**Novo: thesis revision rather than anchoring.** Use the event study to describe how the release changed the stock price relative to the market. Then explain what it cannot tell you: the causal impact of a single announcement, commercial value of a clinical endpoint, or optimal exit price. A re-entry requires updated commercial assumptions; a lower price is not sufficient.

**Duration: quantify the trade-off.** Derive the 0.108-year reduction in assumed portfolio duration from a 2% shift and a 5.4-year duration gap. A 100 bp rise improves the price outcome by approximately 10.8 bp of NAV before costs; a fall reverses the effect. Fees and FX can dominate a small move. The order remains pending until separately reconciled.

## Questions to practise

1. Why is the reconstructed book not a live track record? Decision dates and authored dates differ; the universe and historical narrative have hindsight.
2. Why did the forward gain mostly come from currency? Derive the exact endpoint attribution and identify where the interaction is assigned.
3. Why are three equity ETFs not three independent risks? Their underlying holdings and market factors overlap.
4. Why does ES need caution? Few tail observations, unstable regimes and modelled rather than guaranteed liquidity.
5. Why not maximise Sharpe? No reliable expected-return estimates; repeated selection can overfit a short history.
6. Why not call the best rebalancing rule “optimal”? One selected period and costs cannot validate predictive superiority.
7. What is missing from FX carry? Executable forward points, funding, basis, collateral and EUR accounting.
8. Why can futures lose when spot is flat? A long contract can converge down from a premium; the roll transaction itself is not an instantaneous loss of the price difference.
9. What did the paper change in your implementation? Its warning against a constant-correlation target across asset classes led to a sample baseline and explicit target sensitivities.
10. What would you build next? Current operating models for the few single names, a prospective forecast log and a sourced execution record.

Demonstration: run `python -m investment_lab valuation`, change one assumption in a separate working copy, rerun, and explain the direction of the result. Do the same for one rate shock and one adverse FX move. Preserve the original output when making experiments.
