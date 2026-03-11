# EVT + Conformal Prediction Literature Landscape

**Date:** 2026-03-11
**Claim:** CL-G4 — Extreme Conformal Prediction for Intraday Tail Events
**Scout Type:** Deep dive for positioning

---

## Executive Summary

The EVT+conformal intersection has **one primary competitor** (Pasche et al. 2025) and **several adjacent methods** (RWC, TCP, ACI). CL-G4's wedge remains intact: **nobody has EVT-augmented conformal for high-frequency financial tail events under mixing dependence**.

| Paper | EVT? | Financial? | Mixing? | Threat to CL-G4 |
|-------|------|-----------|---------|-----------------|
| Pasche et al. (2505.08578) | Yes (GPD) | Mentioned only | Weighted extension | **MEDIUM** — methodology overlap |
| Schmitt (2602.03903) | No | Yes (CRSP) | Regime-weighted | LOW — no EVT |
| Aich et al. (2507.05470) | No | Yes (S&P, BTC) | Rolling windows | LOW — no EVT |
| Barber & Pananjady (2510.02471) | No | General | Switch coefficients | LOW — foundational, no EVT |

---

## Paper 1: Pasche, Lam & Engelke (2025) — **PRIMARY COMPETITOR**

**"Extreme Conformal Prediction: Reliable Intervals for High-Impact Events"**
arXiv:2505.08578 (May 2025, revised Nov 2025)

### Core Method

1. **Stage 1:** Train extreme quantile regression Q̂_{1-α}(x) on training data
2. **Stage 2:** Fit GPD to calibration nonconformity scores above threshold u
3. **Extrapolation:** Use GPD to extrapolate conformal correction beyond empirical quantiles
4. **Output:** Conservative CI for extreme quantile via profile likelihood

### Formal Result

**Proposition 3.1:** If [Q_l, Q_u] is a (1-α₂)-CI for the (1-α₁)-quantile, and 1-α ≤ (1-α₁)(1-α₂), then P(S_test ≤ Q_u) ≥ 1-α.

**Key caveat:** Loses finite-sample guarantees. Coverage is asymptotic.

### Assumptions

- Exchangeability of calibration/test (relaxed via weighting)
- GPD tail approximation valid (peaks-over-threshold asymptotics)
- Tail index ξ stationary over calibration period

### Weighted Extension for Nonstationarity

Uses weighted GPD likelihood:
```
ℓ^w_GPD(σ,ξ) with weights w_i ∈ [0,1]
```
For seasonal data: w_i = cos[2π/24{B(i)-b}] + 1 (sinusoidal by season)

### Application Domain

**Environmental only:** Flood forecasting for Aare river (Switzerland). Financial data mentioned ("asset returns at risk of large losses") but **no actual financial experiments**.

### Limitations Acknowledged

1. Overconservative for moderate extremes / light tails
2. No finite-sample guarantees (asymptotic only)
3. Numerical instability with profile likelihood (bootstrap fallback)
4. Marginal coverage only, not conditional

### Positioning vs CL-G4

| Dimension | Pasche et al. | CL-G4 |
|-----------|---------------|-------|
| Domain | Environmental | **Financial (FX, Crypto)** |
| Dependence | Weighted exchangeability | **β-mixing (Barber-Pananjady)** |
| Data frequency | Daily/seasonal | **Intraday/tick** |
| Theory | Asymptotic | **Finite-horizon bounds** |
| Events | Floods, wildfires | **Flash crashes, tail events** |

**Threat level: MEDIUM** — Method is similar, but domain and dependence handling differ.

---

## Paper 2: Schmitt (2026) — Regime-Weighted Conformal (RWC)

**"Taming Tail Risk in Financial Markets: Conformal Risk Control for Nonstationary Portfolio VaR"**
arXiv:2602.03903 (Feb 2026)

### Core Method

- Regime-Weighted Conformal (RWC) calibration
- Safety buffer c^t = weighted quantile of past errors
- Weighting: exponential time decay + regime-similarity kernel

### Data

CRSP value-weighted market index (1990-2024, daily)

### Coverage

Finite-sample under weighted exchangeability (Theorem 5.2)

### Relation to CL-G4

- **No EVT/GPD** — uses empirical quantiles only
- Works for moderate quantiles (95%, 99%), not extreme (99.9%+)
- **Not a competitor** — complementary approach

**Threat level: LOW** — Different method (no EVT), different quantile regime.

---

## Paper 3: Aich et al. (2025) — Temporal Conformal Prediction (TCP)

**"Temporal Conformal Prediction: A Distribution-Free Framework for Adaptive Risk Forecasting"**
arXiv:2507.05470 (July 2025)

### Core Method

- Gradient-boosted quantile + rolling split-conformal
- TCP-RM variant: Robbins-Monro online offset adjustment

### Data

S&P 500, BTC-USD, Gold (Nov 2017 - May 2025)

### Coverage

Finite-sample under local exchangeability in rolling windows

### Relation to CL-G4

- **No EVT** — distribution-free empirical approach
- Works for 95% quantiles, not extreme tails
- Rolling windows, not full-sample GPD extrapolation

**Threat level: LOW** — No EVT component.

---

## Paper 4: Barber & Pananjady (2025) — Switch Coefficients

**"Predictive inference for time series: why is split conformal effective despite temporal dependence?"**
arXiv:2510.02471 (Oct 2025)

### Core Contribution

- Switch coefficient framework for coverage bounds under β-mixing
- Sharp characterization: coverage gap = O(switch_coeff / n)

### Relation to CL-G4

- **Foundational theory** — CL-G4 builds on this
- Does not address extreme quantiles / EVT
- Provides the mixing-dependence bridge CL-G4 needs

**Threat level: LOW (upstream dependency, not competitor)**

---

## Paper 5: Adaptive Conformal for Crypto VaR (MPRA 2024)

**"Adaptive Conformal Inference for Computing Market Risk Measures: Analysis with 4000 Crypto-Assets"**

### Key Finding

FACI and SF-OGD provide best VaR estimates for crypto at moderate quantiles.

### Relation to CL-G4

- Crypto domain overlap
- No EVT — empirical quantiles only
- Moderate quantiles (95%, 97.5%), not extreme

**Threat level: LOW**

---

## CL-G4 Wedge Analysis

### Current Wedge (from CLAIMS_LIBRARY.md)

> "Nobody has EVT-augmented conformal for HF financial tail events."

### Wedge Status: **INTACT but needs sharpening**

### Differentiation Axes

| Axis | Closest Work | CL-G4 Differentiation |
|------|--------------|----------------------|
| **Domain** | Pasche (environmental) | Financial (FX flash crashes, crypto) |
| **Frequency** | All papers (daily) | **Intraday/tick-level** |
| **Dependence** | Pasche (weighted exchangeability) | **β-mixing (Barber-Pananjady switch coefficients)** |
| **Theory** | Pasche (asymptotic) | **Finite-horizon bounds with n_u exceedances** |
| **Events** | Pasche (floods) | **Flash crashes, circuit breakers, tail censoring** |

### Updated Wedge Statement

> CL-G4 is the first to combine EVT-based conformal prediction with the Barber-Pananjady switch coefficient framework for **intraday financial tail events** under β-mixing dependence, providing **finite-horizon coverage bounds** that account for **tail censoring** from circuit breakers.

---

## Actionable Items

1. **Cite Pasche et al. prominently** — acknowledge methodological inspiration, differentiate via domain + dependence
2. **Use Barber-Pananjady as theoretical foundation** — their switch coefficient bounds + our GPD extrapolation
3. **Emphasize intraday frequency** — no competing work at tick/minute level
4. **Address circuit breaker censoring** — unique contribution not in any prior work
5. **Financial empirics essential** — Pasche has none; this is our primary differentiation

---

## References

1. Pasche, O.C., Lam, H., & Engelke, S. (2025). Extreme Conformal Prediction: Reliable Intervals for High-Impact Events. arXiv:2505.08578.
2. Schmitt, M. (2026). Taming Tail Risk in Financial Markets: Conformal Risk Control for Nonstationary Portfolio VaR. arXiv:2602.03903.
3. Aich, A., Aich, A.B., & Jain, D.C. (2025). Temporal Conformal Prediction (TCP): A Distribution-Free Framework for Adaptive Risk Forecasting. arXiv:2507.05470.
4. Barber, R.F., & Pananjady, A. (2025). Predictive inference for time series: why is split conformal effective despite temporal dependence? arXiv:2510.02471.
