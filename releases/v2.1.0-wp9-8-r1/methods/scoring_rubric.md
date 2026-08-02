# Evidence Maturity Scoring Rubric

Status: **Superseded for prospective coding by
`evidence/JOURNAL_NEUTRAL_CODEBOOK_V2_WP9_3.md`.**

This file retains the compact score table used by historical analyses. The
WP9.3 codebook governs all new coding and any future quantitative rebuild. In
particular, unknown, unclear, and not reported are missing evidence and are not
score 0. Scores are reported as five separate evidence layers and are not
combined into an overall readiness score.

## Field Evidence Score

| Score | Definition |
|---:|---|
| 0 | Purely synthetic simulation or benchmark evidence. |
| 1 | Simulation with realistic geology, field-facing monitoring geometry, or synthetic monitoring. |
| 2 | Laboratory, experimental, controlled-release, or semi-field evidence. |
| 3 | Single field case application or comparison. |
| 4 | Multiple field cases or cross-site validation. |

## Physical Consistency Score

| Score | Definition |
|---:|---|
| 0 | Full text explicitly confirms no physical check or constraint. |
| 1 | Physics inherited from simulator labels or discussed qualitatively. |
| 2 | Partial physics loss, simplified physical constraint, or explicit process coverage. |
| 3 | Diagnostic check such as mass balance, pressure residuals, plume volume, or comparable physical validation. |
| 4 | Coupled physical validation across flow, monitoring, and risk variables. |

## Uncertainty Score

| Score | Definition |
|---:|---|
| 0 | Full text explicitly confirms a deterministic workflow with no uncertainty treatment. |
| 1 | Sensitivity or ensemble analysis without probabilistic calibration. |
| 2 | Probabilistic, Bayesian, posterior, or ensemble uncertainty reported. |
| 3 | Calibrated uncertainty or posterior predictive checking. |
| 4 | Calibrated uncertainty propagated into a decision, optimization, MRV, or corrective-action workflow. |

## Transferability Score

| Score | Definition |
|---:|---|
| 0 | Full text explicitly confirms same-distribution-only testing. |
| 1 | Single field case or field-facing evaluation without transfer. |
| 2 | Unseen parameter range or transfer-learning test. |
| 3 | Unseen geology, wells, faults, boundary conditions, or OOD test. |
| 4 | Cross-site or multiple-field transfer validation. |

## Decision Readiness Score

| Score | Definition |
|---:|---|
| 0 | Technical demonstration with no storage decision linkage. |
| 1 | Predicts a storage-relevant variable. |
| 2 | Linked to a storage decision variable. |
| 3 | Tested near a decision threshold or with field uncertainty. |
| 4 | Auditable operational/MRV workflow with documented and demonstrated human or regulatory use. |

## Overall Readiness

The previous weighted overall-readiness calculation is retired. It obscured
which evidence layer was present or missing and allowed strength in one layer
to compensate numerically for absence in another. Report field evidence,
physical consistency, uncertainty, transferability, and decision readiness
separately with their denominators and missingness.

## Decision Criticality Score

For ESR Figure 3, decision criticality is coded from `application_area` using `config/decision_criticality_map.yaml`.

| Score | Definition |
|---:|---|
| 0 | Background, generic method, or review positioning source. |
| 1 | Early screening or exploratory triage. |
| 2 | Characterization or non-operational interpretation. |
| 3 | Decision support affecting monitoring, pressure, capacity, or risk ranking. |
| 4 | Safety-critical operation, leakage response, wellbore risk, geomechanics/seal risk, MRV decision, or injection control. |

## Verification Status And Unknown Handling

For ESR-level synthesis, scores must distinguish four states:

| State | Meaning | Use in main quantitative figures |
|---|---|---|
| confirmed absence | Full text or explicit source states that the item is absent or not used | May be scored as 0 |
| unknown | The matrix does not contain enough evidence to code the item | Must be NA, not 0 |
| metadata-inferred | Coded from title, abstract, metadata, or project notes without full-text extraction | Use only in screening/supplementary audits unless explicitly labelled |
| full-text verified | Coded from full-text reading or verified local PDF extraction | Eligible for main ESR quantitative synthesis |

Unknown is absence of evidence, not evidence of absence. Main quantitative figures should use full-text verified primary ML-CGS records; metadata-level records should be reported as coverage gaps or supplementary screening maps.

