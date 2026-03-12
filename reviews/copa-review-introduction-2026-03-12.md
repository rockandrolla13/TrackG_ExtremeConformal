# COPA Review: Introduction Draft

**Manuscript:** Extreme Conformal Prediction for Intraday Tail Events
**Review Date:** 2026-03-12
**Review Scope:** Introduction + Abstract only (other sections not yet written)
**Overall Assessment:** Promising direction with clear COPA fit, but several claims need careful handling

---

## COVERAGE CLAIM AUDIT

| Location | Claim | Type | Supported? | Issue |
|----------|-------|------|------------|-------|
| Abstract | "coverage guarantees under β-mixing" | marginal, asymptotic | TBD | Must prove Theorem in §4 |
| Abstract | "coverage bound decomposes as O(β(τ) + n_u^{-1/2})" | marginal, asymptotic | TBD | Explicit bound promised — must deliver |
| Abstract | "maintaining nominal coverage" (empirics) | marginal, empirical | TBD | Must verify in §6 |
| ¶1 | "finite-sample coverage guarantees" | finite-sample | **CAUTION** | Only under exchangeability; paper handles mixing which is asymptotic |
| ¶2 | "conformal coverage guarantees under temporal dependence" (Barber-Pananjady) | marginal, finite-sample | Yes | Correctly attributed |
| ¶3 | "coverage gap bounded by O(β(τ) + n_u^{-1/2})" | marginal, asymptotic | TBD | Core claim — Theorem must establish |
| ¶5 | "coverage bound (Theorem X) decomposes into mixing error O(β(τ)) and estimation error O(n_u^{-1/2})" | marginal, asymptotic | TBD | Forward reference — must prove |
| ¶5 | "achieves the nominal coverage" (empirics) | marginal, empirical | TBD | Must verify experimentally |

### Coverage Claim Summary

**Good:** Claims are mostly correctly typed (marginal, asymptotic). The bound decomposition is clear.

**Concern:** ¶1 mentions "finite-sample coverage guarantees" for conformal prediction generally, but the paper's contribution is under mixing, which Barber-Pananjady shows is *not* finite-sample exact. The introduction correctly notes this later, but the framing could mislead.

**Missing:** No explicit statement about conditional coverage. This is good (don't overclaim), but should explicitly note that guarantees are marginal only.

---

## INTRODUCTION ASSESSMENT

### Structure (Score: 8/10)

The introduction follows a clear arc:
1. Problem (extreme quantiles, regulatory need)
2. Literature gap (Pasche = EVT+CP but exchangeable; B&P = mixing but no EVT)
3. Key insight (composition of GPD + switch coefficients)
4. Additional challenge (circuit breaker censoring)
5. Contributions (four numbered)
6. Related work (comprehensive)
7. Paper structure

**Good:** Logical flow, clear gap identification, numbered contributions.

**Issue:** ¶4 (circuit breaker censoring) slightly disrupts flow — it's a contribution but framed as a "complication." Consider merging into contributions paragraph or moving to §3.

### COPA-Specific Signals

**POSITIVE:**
- [x] Novel conformity measure principle (GPD-extrapolated scores)
- [x] Explicit discussion of exchangeability violation (mixing)
- [x] Connection to Barber-Pananjady switch coefficient framework
- [x] Impossibility result promised (Proposition) — COPA values this
- [x] Real-data application promised (FX + crypto)
- [x] Honest scoping: "delimits when our method applies"

**NEGATIVE:**
- [ ] No mention of Vovk's conditional coverage impossibility (should cite Vovk 2012 in related work)
- [ ] No comparison to CQR baseline mentioned (standard COPA expectation)
- [ ] Missing: explicit statement that coverage is marginal, not conditional

### Related Work Assessment (Score: 7/10)

**Good coverage of:**
- EVT foundations (Pickands, Balkema, McNeil, Embrechts)
- Conformal under dependence (Barber-Pananjady, Oliveira, ACI)
- Financial applications (Schmitt, Kato)
- Circuit breaker literature (Subrahmanyam, Kim)

**Missing:**
- Vovk, Gammerman & Shafer (2005) — foundational CP book
- Vovk (2012) — conditional coverage impossibility
- Romano, Patterson & Candès (2019) — CQR baseline
- Lei & Wasserman (2014) — distribution-free predictive inference

**Recommendation:** Add these four citations to related work. COPA reviewers will expect them.

---

## CLAIM VERIFICATION CHECKLIST

Claims made in introduction that require support in later sections:

| Claim | Required Support | Section |
|-------|------------------|---------|
| Coverage bound O(β(τ) + n_u^{-1/2}) | Theorem with proof | §4 |
| GPD + switch coefficients "compose naturally" | Formal argument | §3 or §4 |
| Censoring correction extends GPD likelihood | Algorithm/equation | §3 |
| Impossibility under homoscedastic tails | Proposition with proof | §4 |
| 30-50% narrower intervals | Empirical tables | §6 |
| Nominal coverage maintained | Coverage tables with SE | §6 |
| Works on FX flash crashes | Empirical results | §6 |
| Works on crypto crashes | Empirical results | §6 |

---

## SPECIFIC ISSUES

### Issue 1: Finite-sample vs. Asymptotic Framing (Priority: HIGH)

**Location:** ¶1, ¶3

**Problem:** ¶1 emphasizes "finite-sample coverage guarantees" as a strength of conformal prediction, but under mixing the guarantee is asymptotic (Barber-Pananjady bound has O(1/n) terms). ¶3's bound O(β(τ) + n_u^{-1/2}) is not finite-sample exact.

**Fix:** Clarify that the contribution provides *explicit, computable* coverage bounds under dependence, not finite-sample exact guarantees. The practical value is that the bound is tight enough to be useful, not that it's exact.

### Issue 2: Missing Conditional Coverage Disclaimer (Priority: MEDIUM)

**Location:** Throughout

**Problem:** All coverage claims are marginal, but this isn't stated explicitly. COPA reviewers will want clarity.

**Fix:** Add one sentence in ¶5: "Our guarantees are marginal; we do not claim conditional coverage, which is impossible without distributional assumptions (Vovk, 2012)."

### Issue 3: Circuit Breaker Paragraph Placement (Priority: LOW)

**Location:** ¶4

**Problem:** ¶4 introduces circuit breaker censoring as a "practical complication" between the key insight (¶3) and contributions (¶5). This breaks the flow.

**Options:**
- (a) Move to §3 (Method) where the correction is developed
- (b) Integrate into ¶5 as contribution #2 (currently done, but ¶4 is redundant)
- (c) Keep but shorten ¶4 to 2 sentences

### Issue 4: Empirical Claims Specificity (Priority: MEDIUM)

**Location:** ¶5

**Problem:** "30--50% narrower intervals" is precise but "achieves the nominal coverage" is vague. What is nominal? 90%? 99%? 99.9%?

**Fix:** Specify: "achieves 99.9% nominal coverage (±0.5pp in empirical validation)."

### Issue 5: Missing CQR Baseline (Priority: HIGH for COPA)

**Location:** Related work

**Problem:** No mention of Conformalized Quantile Regression (Romano et al. 2019), which is the standard CP baseline for interval estimation. COPA reviewers will expect comparison.

**Fix:** Add to related work and note that CQR also suffers from the infinite-interval problem at extreme quantiles.

---

## AUTOMATIC FLAGS CHECK

- [ ] Any claim of "exact conditional coverage" without exchangeability — **PASS** (no such claim)
- [ ] Any claim of "finite-sample coverage" under dependence without qualification — **FLAG** (¶1 mentions finite-sample for CP generally; clarify this doesn't apply under mixing)
- [x] Missing comparison to at least one standard CP baseline — **FLAG** (CQR not mentioned)
- [x] No discussion of the exchangeability assumption — **PASS** (discussed in ¶2)
- [x] Undefined or inconsistent notation for conformity scores — **N/A** (no notation yet in intro)
- [ ] Coverage experiments without standard errors — **N/A** (no experiments yet)
- [x] Mixing marginal and conditional coverage language — **PASS** (all claims appear marginal)

---

## REVISION CHECKLIST

### Before Writing §2-§7

- [ ] **P1 (High):** Add Vovk (2012) conditional coverage impossibility citation; note guarantees are marginal
- [ ] **P1 (High):** Add Romano et al. (2019) CQR citation and note it shares the extreme-quantile limitation
- [ ] **P2 (Medium):** Clarify finite-sample vs. asymptotic in ¶1 — bound is explicit but not exact under mixing
- [ ] **P2 (Medium):** Specify "99.9% nominal coverage" instead of vague "nominal coverage"
- [ ] **P3 (Low):** Consider shortening ¶4 (circuit breaker) — detail belongs in §3
- [ ] **P3 (Low):** Add Lei & Wasserman (2014) and Vovk, Gammerman & Shafer (2005) to related work

### Theoretical Obligations Created

The introduction promises:
1. **Theorem (coverage bound):** Must prove O(β(τ) + n_u^{-1/2}) decomposition
2. **Proposition (impossibility):** Must prove GPD cannot help under homoscedasticity
3. **Algorithm (censoring):** Must specify truncation-corrected GPD likelihood
4. **Experiments:** Must show coverage + width on FX + crypto with documented extreme events

---

## OVERALL VERDICT

**For an introduction draft:** Strong. Clear problem statement, well-identified gap, crisp contributions, comprehensive related work. The COPA-specific content (exchangeability discussion, impossibility result, real-data validation) signals appropriate venue fit.

**Main concerns:**
1. Finite-sample framing needs nuance
2. Missing foundational CP citations (Vovk 2012, CQR)
3. Should explicitly state "marginal coverage only"

**Recommendation:** Address P1 items before writing theory section, as they affect how Theorem 1 should be stated.
