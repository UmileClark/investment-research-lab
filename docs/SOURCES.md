# Evidence register

The reports link each model to its relevant source and explain whether the application is implemented mathematics, a sensitivity diagnostic or conceptual motivation. Papers do not certify these particular holdings or their expected returns. Full papers are not redistributed.

## Model sources

- **Ledoit & Wolf (2003 working paper; 2004 journal publication), Honey, I Shrunk the Sample Covariance Matrix.** https://econ-papers.upf.edu/papers/691.pdf. Pages 5–6 describe the constant-correlation target; footnote 4 cautions against applying it across asset classes. This package uses sample covariance as its baseline and compares fixed shrinkage targets; it does not estimate optimal Ledoit-Wolf shrinkage.
- **DeMiguel, Garlappi & Uppal (2009), Optimal versus Naive Diversification.** https://doi.org/10.1093/rfs/hhm075. Benchmark motivation concerning estimation error. The three-rule experiment is not a replication of their study.
- **Brunnermeier, Nagel & Pedersen (2008), Carry Trades and Currency Crashes.** https://markus.scholar.princeton.edu/publications/carry-trades-and-currency-crashes. Motivates funding-unwind stress; no claim that the project's two crosses reproduce their sample.
- **Borio, McCauley, McGuire & Sushko (2016), Covered Interest Parity Lost.** https://www.bis.org/publ/qtrpdf/r_qt1609e.htm. Explains why actual forward markets can deviate from zero-basis textbook parity. The project does not estimate basis.
- **Damodaran, Investment Valuation, chapter 14, Free Cash Flow to Equity Discount Models.** https://pages.stern.nyu.edu/~adamodar/pdfiles/valn2ed/ch14.pdf. Valuation framework. The simplified CFO-capex-SBC proxy omits a full financing forecast.
- **Adrian, Crump & Moench, Pricing the Term Structure with Linear Regressions.** https://www.newyorkfed.org/research/staff_reports/sr340.html. Distinguishes rate expectations and term compensation. No ACM term-premium estimates are fitted.
- **Gorton & Rouwenhorst, Facts and Fantasies about Commodity Futures (2004 working paper; 2006 publication).** https://www.nber.org/papers/w10595. The published author-hosted copy is https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/20/2020/12/Facts-and-Fantasies-about-Commodity-Futures.pdf. Broad collateralised-index results do not establish the properties of one fund or one commodity.
- **Erb & Harvey (2013), The Golden Dilemma.** https://www.nber.org/papers/w18706. Motivation for caution about inflation-hedge claims.
- **Liu & Tsyvinski (2018), Risks and Returns of Cryptocurrency.** https://www.nber.org/papers/w24877. Early crypto evidence; no assumption that sample relationships are stable.
- **MacKinlay (1997), Event Studies in Economics and Finance.** Journal of Economic Literature 35(1), 13–39. https://www.jstor.org/stable/2729691. Market-model abnormal-return framework. Our three ex-post events are descriptive, with no causal or statistical-significance claim.
- **Bailey, Borwein, López de Prado & Zhu (2015), The Probability of Backtest Overfitting.** https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf. Motivates reporting every tried rule and cost assumption. No PBO estimate is claimed from this small comparison.

## Numerical anchors

**CME FY2023 annual report**, filed February 2024, https://www.sec.gov/Archives/edgar/data/1156375/000115637524000010/cme-20231231.htm. The cash-flow statement reports CFO 3,453.8m, property purchases 76.4m and SBC 82.9m. The EPS note reports diluted weighted-average common shares of 359,500 thousand; the equity statement reports 4,584 thousand participating preferred shares. These are all USD or share units specified in `DATA_DICTIONARY.md`.

**RBA 24 September 2024:** https://www.rba.gov.au/media-releases/2024/mr-24-18.html, cash-rate target 4.35%.

**BOJ 20 September 2024:** https://www.boj.or.jp/en/mopo/mpmdeci/state_2024/k240920a.htm, overnight-call-rate target around 0.25%. The statement was available then; later minutes are not substituted for the original information set.

**Banxico 26 September 2024:** https://www.banxico.org.mx/canales/%7BA49B18D6-DC38-7FBE-9345-192D1E922B2A%7D.pdf, target reduced to 10.50%, effective 27 September. These policy rates only anchor a teaching example; matching deposit/loan rates and executable forward points are absent.

Novo's releases of 20 December 2024 and 29 July 2025 and Rheinmetall's release of 12 March 2025 are preserved with exact source URLs in `data/book.json` and the event report. They identify release dates; they do not prove that the entire measured abnormal return was caused by one announcement.

## Access and provenance

Sources were reviewed or carried forward from the existing evidence register on 28 September 2026. Some publisher/PDF endpoints restrict automated access; the bibliography retains their stable primary references. Dates in the paper descriptions are publication dates, not retrieval dates. Price archives retain provider retrieval fields and are checked against frozen SHA-256 hashes.


## 3 October 2026 additions

- [BCBS (2018), Stress testing principles](https://www.bis.org/bcbs/publ/d450.htm): Scenario design and governance motivation. The four assumed shocks are not a regulatory stress test or estimated crisis probabilities.
- [Moskowitz, Ooi & Pedersen (2012), Time Series Momentum](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum): Motivates lagged own-return signals. Our monthly long/cash ETF rule is not a replication of the paper’s futures strategy.
- [Moreira & Muir (2016/2017), Volatility-Managed Portfolios](https://www.nber.org/papers/w22208): Motivates exposure sensitivity to realised volatility. Our capped volatility target differs from the paper’s inverse-variance factor portfolios.
- [Newey & West (1986/1987), A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix](https://www.nber.org/papers/t0055): OLS coefficient uncertainty uses a Bartlett-weighted HAC estimator with five lags. Approximate intervals do not establish causal exposures.
- [Chekhlov, Uryasev & Zabarankin (2005), Drawdown Measure in Portfolio Optimization](https://researchconnect.stonybrook.edu/en/publications/drawdown-measure-in-portfolio-optimization/): Motivates path-dependent loss analysis. The project measures episodes and block-resampling sensitivity; it does not solve the paper’s optimisation problem.
- [Basel Framework MAR32, Backtesting requirements](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/32/inforce/2023-01-01/published/2020-03-27): Motivates comparison of lagged risk forecasts with subsequent losses. Coverage diagnostics here are educational, not a regulatory backtest or model certification.
- [Black & Scholes (1973), The Pricing of Options and Corporate Liabilities](https://doi.org/10.1086/260062): European call/put pricing at assumed constant volatility, with put–call parity tested. No market-implied volatility or tradable quote is inferred.
- [Cboe (2021), Hedging Downside Exposure with PPUT, CLL and CLLZ Indices](https://www.cboe.com/insights/posts/benchmark-indices-series-hedging-downside-exposure-with-pput-cll-and-cllz-indices/): Institutional context for protective puts and collars. Synthetic strikes and costs do not replicate a Cboe benchmark.
- [Gneiting & Raftery (2007), Strictly Proper Scoring Rules, Prediction, and Estimation](https://doi.org/10.1198/016214506000001437): Motivates recording probabilities before outcomes and scoring with binary Brier loss. A theoretical demonstration is kept separate from personal evidence.
