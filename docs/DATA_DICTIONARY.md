# Data and conventions

| File | Contents | Time meaning |
|---|---|---|
| book.json | Inception allocation, ten pitches, dated retrospective decisions and primary sources | Authored in 2026; historical information cutoffs explicit |
| historical_book.json | Reconstructed holdings, cash, trades, daily NAV and reviews | 30 September 2024–18 September 2026 |
| current_book.json | Fixed-share marks, forward review and pending paper instruction | Marks 25 September; published 28 September 2026 |
| training_prices.json | Adjusted and raw daily marks, FX and retrieval metadata | Market observations 2021–27 September 2024; retrieved 2026 |
| historical_prices.json | Adjusted and raw daily marks; FX crosses and metadata | Historical study quotes; retrieved 2026 |
| forward_prices.json | Raw/adjusted prices and corporate actions around handover | Study uses 18–25 September 2026 only |
| manifest.json | SHA-256 for the six frozen JSON files | Integrity check, not an independent timestamp authority |

FX: `EURUSD=X` is USD per EUR. Convert a USD price to EUR by dividing by EURUSD. The attribution uses its inverse, EUR per USD. AUDJPY and MXNJPY are JPY per unit of the target currency. Those series measure spot risk only.

Historical holdings are total-return index units based on vendor adjusted prices; they are not shares that could have been traded at the adjusted quote. At handover, index units are converted to equivalent shares using adjusted/raw close. The forward book uses those fixed equivalents with unadjusted closes. No distribution with an ex-date after handover and by the current mark date was found in the snapshot for a funded holding.

Common-date panels require observations for all selected instruments and FX. Europe, US and crypto closes remain asynchronous. Weekends are excluded for common panels; no interpolation or future filling is used. The accounting replay follows the original weekday valuation calendar with a five-calendar-day stale-quote guard. Rule comparisons use common-market dates and therefore can report different volatility/drawdown sampling from the original weekday ledger.

The event-study loader rescales older adjusted-price levels to the newer archive at 27 September 2024, preserving older within-archive returns. The overlap is a revision bridge, not a claim of vendor point-in-time purity. Source hashes prove which downloaded inputs were used; they cannot prove that those inputs were available unchanged in 2024.

CME inputs are USD millions: CFO 3,453.8; purchases of property 76.4; cash-flow-statement SBC 82.9; diluted weighted-average common shares 359.500m; participating preferred shares 4.584m. The total denominator of 364.084m spreads the cash proxy across common and participating claims. It is a conservative allocation convention, not a complete preferred-security valuation. No net cash is added to a cash-flow proxy already affected by financing/investment income.

Rates, weights and returns in JSON/CSV use decimals. P&L amounts are EUR except the valuation's explicitly USD share values and FX's dimensionless JPY-notional payoff. Commodity curve examples are synthetic. Pending trade scenarios are not booked returns.
