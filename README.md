# Statistical Arbitrage: Pairs Trading via Cointegration  
## A Quantitative Study on SPY–IVV

---

## Overview

This project implements a **statistical arbitrage (pairs trading)** strategy based on **cointegration and mean reversion**, using **SPY** and **IVV** — two highly liquid ETFs tracking the S&P 500 index.

The objective is **not** to maximise raw returns, but to rigorously test:

- Whether statistically significant relationships translate into **tradable alpha**
- How **transaction costs** affect viability
- Where the **limits of statistical arbitrage** lie in highly efficient markets

**SPY–IVV** is deliberately used as a *control pair* representing near-perfect market efficiency.

---

## TL;DR for Quants

- Strong cointegration confirmed (ADF p-value < 0.001)
- Stable hedge ratio (β ≈ 1, low variance)
- Mean reversion exists but deviations are economically small
- Pre-cost Sharpe ≈ **+0.08**
- Break-even execution ≈ **0.8 bps**
- After realistic costs, alpha is fully absorbed
- Demonstrates the **limits of stat arb in highly efficient markets**

---

## Economic & Statistical Rationale

SPY and IVV track the same underlying index with nearly identical holdings and weights.  
Any persistent divergence should be short-lived, making the pair a clean benchmark for testing mean-reversion mechanics under realistic trading assumptions.

---

## Methodology

### 1. Data

- Daily adjusted close prices (2014–2026)
- Source: **Yahoo Finance** (`yfinance`)
- Log prices and log returns used throughout

---

### 2. Pair Validation

An initial candidate (**KO–PEP**) was tested and rejected due to:

- Lack of cointegration (ADF p ≈ 0.40)
- Unstable hedge ratios

**SPY–IVV** was selected based on both **economic structure** and **statistical evidence**.

---

### 3. Cointegration Testing (Engle–Granger)

$$
\log(P_t^{SPY}) = \alpha + \beta \log(P_t^{IVV}) + \varepsilon_t
$$

- Estimated hedge ratio: **β ≈ 0.999**
- Augmented Dickey–Fuller test on residual spread:
  - **p-value ≈ 0.000045**
- Conclusion: **Strong cointegration**

A rolling 252-day regression confirms that the hedge ratio remains highly stable across regimes, including periods of market stress.

---

### 4. Signal Construction

- Spread normalised using rolling z-scores (60-day window)
- Conservative thresholds chosen to limit overtrading

**Trading rules (optimised):**

- Enter long spread: $z < -3.0$

- Enter short spread: $z > +3.0$

- Exit: $|z| \le 0$

- Stop-loss: $|z| > 6.0$

- Max holding period: **30 days**

Positions are **dollar-neutral**, hedged using the estimated β.

---

### 5. Backtesting Framework

- Strict time-based split
  - **Train:** 2014–2022 (parameter estimation)
  - **Test:** 2022–2026 (out-of-sample only)
- Hedge ratio estimated on training data only
- Transaction costs applied **per leg**
- No parameter tuning on test data

---

## Headline Out-of-Sample Results (2022–2026)

| Metric | Value |
|------|------|
| Sharpe (2 bps costs) | **-0.16** |
| Total Return | **-0.45%** |
| Max Drawdown | **-1.27%** |
| Trades | **36** |
| Exposure | **11.8%** |
| Break-even cost | **~0.8 bps** |

Full diagnostics and sensitivity analysis are available in `/reports`.

---

## Transaction Cost Sensitivity

| Cost Assumption | Sharpe | Viability |
|----------------|--------|-----------|
| 0 bps | **+0.08** | Profitable |
| 2 bps | **-0.16** | Near breakeven |
| 5 bps | **-0.46** | Unprofitable |

Even with statistically strong signals, **execution costs dominate** for extremely tight spreads such as SPY–IVV.

---

## Interpretation

The results are **expected and correct**.

SPY–IVV represents an exceptionally efficient market pair:

- Cointegration and mean reversion are present
- Mispricings are too small to survive realistic transaction costs

Rather than indicating failure, the strategy **validates market efficiency** and highlights the practical boundary between **statistical significance** and **tradable alpha**.

---

## Limitations

- Results specific to a single, highly efficient pair
- Fixed execution cost model
- No regime filtering (e.g. volatility-based)
- Limited out-of-sample length (~3.6 years)

---

## Extensions & Future Work

- Apply identical framework to less efficient pairs (sector ETFs, single stocks)
- Portfolio of multiple cointegrated pairs
- Walk-forward estimation
- Regime-aware filters (e.g. VIX-based)
- Intraday data and execution modelling

---

## Repository Structure
```
├── data/
├── notebooks/
│ ├── 01_universe_and_data.ipynb
│ ├── 02_pair_selection.ipynb
│ ├── 03_cointegration_tests.ipynb
│ ├── 04_signal_and_sizing.ipynb
│ ├── 05_backtest.ipynb
│ └── 06_results_report.ipynb
├── src/
│ ├── data.py
│ ├── tests.py
│ ├── signals.py
│ ├── backtest.py
│ └── metrics.py
└── reports/
```

---

## Key Takeaway

**Statistical significance does not guarantee tradable alpha.**  
In highly efficient markets, transaction costs dominate even well-behaved mean-reversion signals.

This project demonstrates **quantitative research discipline**, not overfitted performance.

---

## Notes for Reviewers

Interview discussion notes and extended diagnostics are available in `/reports`.

---

## License

This project is licensed under the MIT License - see the [LICENSE](#license) file for details.

---

## Disclaimer

This project is for **educational and research purposes only**.  
It is **not financial advice**.
