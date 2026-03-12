# COPA Review: Introduction Draft (Revised)

**Manuscript:** Extreme Conformal Prediction for Intraday Tail Events
**Review Date:** 2026-03-12
**Review Scope:** Introduction + Abstract only (other sections not yet written)
**Overall Assessment:** Clear problem statement with strong COPA fit; revision successfully eliminates overlap with related work

---

## OVERALL ASSESSMENT

This revised introduction establishes a clean research contribution: extending EVT-based conformal prediction (Pasche et al. 2025) to temporally dependent financial data via β-mixing corrections. The framing now focuses squarely on the **sample-size-vs-confidence-level mismatch** (α < 1/(n+1) forces infinite-width intervals), which is the correct problem statement for extreme conformal prediction. The impossibility result about tail shape (not heteroscedasticity) provides appropriate scope delimitation. Strong fit for COPA given the novel conformity measure principle and explicit treatment of exchangeability violation.

---

## REVISION ASSESSMENT: Overlap Elimination

The revision successfully addresses the overlap concerns with TrackF (Kernel Conformity):

| Aspect | Previous Version | Revised Version | Status |
|--------|------------------|-----------------|--------|
| Core problem | Heteroscedasticity + extreme quantiles | Sample size vs confidence level | ✓ Fixed |
| Impossibility framing | Heteroscedasticity (overlapped with TrackF) | Tail shape (ξ > 0 vs ξ ≤ 0) | ✓ Fixed |
| Switch coefficients | Prominent, parallel to TrackF | Mentioned once as literature | ✓ Fixed |
| Barber-Pananjady role | Central contribution | One input among two orthogonal pieces | ✓ Fixed |
| GARCH/regime language | Present | Removed entirely | ✓ Fixed |

**The two papers now have clearly distinct identities:**
- **TrackF:** "Design conformity scores that are more exchangeable under heteroscedasticity"
- **TrackG:** "Extrapolate the score distribution to reach extreme quantiles under mixing"

---

## SCORING (1-10 scale, introduction-only assessment)

### Criterion 1: Conformal Prediction Relevance (weight: 15%)
**Score:** 9/10
**Justification:** Novel CP principle: GPD extrapolation of conformity score distribution to break the α < 1/(n+1) barrier. This addresses a fundamental limitation of standard conformal methods at extreme quantiles.

### Criterion 2: Theoretical Contribution (weight: 15%)
**Score:** N/A (TBD) → Projected 7-8/10
**Justification:** Introduction promises coverage bound O(β(τ) + n_u^{-1/2}) with additive decomposition. If proved, this is a solid non-trivial result. Impossibility for light tails adds theoretical completeness.

### Criterion 3: Methodological Clarity (weight: 10%)
**Score:** 8/10
**Justification:** Core idea is clear: GPD extrapolation on conformity scores + mixing correction. The censoring correction for circuit breakers is well-motivated. Algorithm details deferred to method section.

### Criterion 4: Experimental Design (weight: 10%)
**Score:** N/A (TBD)
**Justification:** Introduction promises FX flash crashes (SNB, Brexit, JPY) and cryptocurrency collapses (COVID, FTX). Good selection of documented extreme events.

### Criterion 5: Empirical Results Quality (weight: 10%)
**Score:** N/A (TBD)
**Justification:** Claims 30-50% narrower intervals while maintaining nominal coverage. Must verify in §6.

### Criterion 6: Honesty and Integrity (weight: 10%)
**Score:** 9/10
**Justification:** The impossibility result (GPD cannot help for light tails) is excellent scope delimitation. Explicit statement that guarantees are marginal (Vovk 2012 cited). No overclaiming.

### Criterion 7: Writing Quality (weight: 10%)
**Score:** 9/10
**Justification:** Clear logical flow: problem → literature gap → key insight → complication → contributions → related work → structure. Equation (1) provides crisp formal statement of the main bound.

### Criterion 8: Novelty (weight: 10%)
**Score:** 8/10
**Justification:** Pasche et al. (2025) did EVT+conformal for environmental extremes under exchangeability; this extends to mixing. Not "surprising" but fills a clear gap.

### Criterion 9: Significance and Impact (weight: 5%)
**Score:** 7/10
**Justification:** High practical value for financial risk management at regulatory quantiles (99.9%+). Niche but important problem.

### Criterion 10: Reproducibility (weight: 5%)
**Score:** N/A (TBD)
**Justification:** No code yet. Must provide replication package.

### WEIGHTED TOTAL (assessable criteria only)

Based on assessable introduction elements:
- C1 (CP relevance): 9
- C3 (clarity): 8
- C6 (honesty): 9
- C7 (writing): 9
- C8 (novelty): 8
- C9 (significance): 7

**Introduction-Only Score: 8.3/10** (Strong Accept potential if theory/experiments deliver)

---

## COVERAGE CLAIM AUDIT

| Location | Claim | Type | Supported? | Issue |
|----------|-------|------|------------|-------|
| Abstract | "coverage guarantees under β-mixing" | marginal, asymptotic | TBD | Must prove Theorem in §4 |
| Abstract | "coverage bound decomposes as O(β(τ) + n_u^{-1/2})" | marginal, asymptotic | TBD | Explicit bound promised |
| Abstract | "maintaining nominal coverage" (empirics) | marginal, empirical | TBD | Must verify in §6 |
| ¶1 | "P(Y_{n+1} ∈ Ĉ) ≥ 1-α under exchangeability" | marginal, finite-sample | Yes | Standard CP; correctly stated |
| ¶3 | Eq (1): coverage gap bounded | marginal, asymptotic | TBD | Core claim; Theorem required |
| Related | "marginal" coverage (Vovk 2012 conditional impossibility cited) | marginal only | Yes | Correctly disclaimed |

### Coverage Claim Summary

**Good:**
- All claims correctly typed as marginal, not conditional
- Vovk (2012) conditional impossibility cited
- Bound structure (mixing + estimation) is well-separated

**Fixed from previous version:**
- ¶1 no longer emphasizes "finite-sample" in misleading way
- The claim is now that GPD extrapolation + mixing correction gives *explicit, computable* bounds, not exact finite-sample guarantees

---

## AUTOMATIC FLAGS CHECK

- [x] Any claim of "exact conditional coverage" without exchangeability — **PASS** (no such claim)
- [x] Any claim of "finite-sample coverage" under dependence — **PASS** (now clearly asymptotic)
- [x] Missing comparison to at least one standard CP baseline — **PASS** (CQR now cited in related work)
- [x] No discussion of exchangeability assumption — **PASS** (¶2 discusses violation)
- [x] Undefined notation for conformity scores — **N/A** (no notation in intro)
- [x] Coverage experiments without standard errors — **TBD** (not written yet)
- [x] Mixing marginal/conditional language — **PASS** (all claims marginal)

**All flags cleared for introduction.**

---

## COPA-SPECIFIC SIGNALS

### POSITIVE Signals Present
- [x] **Novel conformity measure principle:** GPD extrapolation on conformity scores
- [x] **Explicit discussion of exchangeability violation:** β-mixing treatment
- [x] **Real-data application promised:** FX + crypto flash crashes
- [x] **Negative/impossibility result:** GPD doesn't help for light tails (ξ ≤ 0)
- [x] **Connection to Barber-Pananjady:** Coverage under mixing
- [x] **Vovk (2012) cited:** Conditional coverage impossibility

### NEGATIVE Signals Absent
- [x] Paper clearly CP-specific; not generic ML
- [x] No theory-experiment contradiction (experiments TBD)
- [x] No overclaiming conditional coverage
- [x] Real data promised, not simulation-only
- [x] CQR baseline mentioned

---

## RELATED WORK ASSESSMENT (Score: 9/10)

**Now includes:**
- Vovk (2012) — conditional coverage impossibility ✓ (added)
- Romano et al. (2019) — CQR baseline ✓ (added)
- Barber & Pananjady (2025) — conformal under mixing ✓
- Pasche et al. (2025) — extreme conformal (exchangeable) ✓
- Zaffran et al. (2022) — adaptive conformal for time series ✓
- Xu & Xie (2023) — sequential conformal ✓ (added)
- EVT foundations (Pickands, Balkema, McNeil, Embrechts) ✓
- Financial applications (Schmitt, Cont stylized facts) ✓

**Still missing (minor):**
- Lei & Wasserman (2014) — distribution-free predictive inference
- Vovk, Gammerman & Shafer (2005) — foundational CP book

**Verdict:** Related work is now comprehensive for COPA standards.

---

## TOP 3 STRENGTHS

1. **Clear problem-contribution alignment:** The α < 1/(n+1) barrier is a real limitation; GPD extrapolation is the right tool; contribution is well-scoped.

2. **Correct coverage claim typing:** All claims are marginal and asymptotic; Vovk (2012) impossibility cited; no overclaiming.

3. **Clean separation from related work:** No longer overlaps with kernel-based conformity score design (TrackF) or pure mixing analysis (Barber-Pananjady).

---

## TOP 3 AREAS FOR THEORY SECTION

1. **Theorem 1 (coverage bound):** Must prove O(β(τ) + n_u^{-1/2}) with explicit constants C₁, C₂. Barber-Pananjady provides mixing term; GPD estimation error needs separate analysis.

2. **Proposition (impossibility):** Must formalize "GPD extrapolation cannot improve on empirical maximum for ξ ≤ 0." This is about concentration of light-tailed maxima.

3. **Censoring correction:** Must specify truncated GPD likelihood and show it doesn't break coverage guarantee.

---

## QUESTIONS FOR THE AUTHORS

1. **Constants C₁, C₂:** Are these explicit and computable, or big-O hiding constants? Practitioners need actual values for the guarantee to be useful.

2. **Threshold selection:** How is the GPD threshold u chosen? Threshold selection in EVT is notoriously subjective; does this affect coverage?

3. **Mixing coefficient estimation:** β(τ) appears in the bound, but how is it estimated in practice? Is the bound actually computable for a given dataset?

---

## REVISION CHECKLIST

### Completed in This Revision
- [x] **P1:** Eliminate heteroscedasticity framing (moved to TrackF)
- [x] **P1:** Make impossibility about tail shape, not volatility
- [x] **P1:** Add Vovk (2012) conditional coverage impossibility citation
- [x] **P1:** Add Romano et al. (2019) CQR citation as baseline
- [x] **P2:** De-emphasize switch coefficients (now one mention)
- [x] **P2:** Remove GARCH/regime language entirely

### Before Writing Theory Section
- [ ] **P1:** Prove Theorem 1 with explicit bound decomposition
- [ ] **P1:** State all assumptions precisely (β-mixing rate, GPD regularity, threshold conditions)
- [ ] **P2:** Formalize impossibility proposition for light tails
- [ ] **P2:** Specify censoring-corrected GPD likelihood
- [ ] **P3:** Add Lei & Wasserman (2014) to references

### Theoretical Obligations Created by Introduction

| Promise | Required Deliverable | Section |
|---------|---------------------|---------|
| Coverage bound O(β(τ) + n_u^{-1/2}) | Theorem with proof | §4 |
| "Decomposes additively" | Explicit proof of additive structure | §4 |
| Impossibility for ξ ≤ 0 | Proposition with proof | §4 |
| Censoring correction | Algorithm + likelihood equation | §3 |
| 30-50% narrower intervals | Empirical tables | §6 |
| Nominal coverage maintained | Coverage tables with SE | §6 |
| FX flash crash validation | SNB/Brexit/JPY results | §6 |
| Crypto crash validation | COVID/FTX results | §6 |

---

## OVERALL VERDICT

**For introduction draft:** Excellent revision. The paper now has a clear, distinct identity focused on the sample-size-vs-confidence-level problem. All COPA-specific requirements are met: novel conformity measure principle, honest scope delimitation, correct coverage claim typing, comprehensive related work. The overlap with TrackF is eliminated.

**Recommendation:** Proceed to theory section. The introduction sets up obligations that must be fulfilled, particularly:
1. Theorem 1 with explicit constants (not just big-O)
2. Impossibility proposition for light tails
3. Censoring correction algorithm

**Projected final score if executed well:** 8.0-8.5 (Strong Accept)
