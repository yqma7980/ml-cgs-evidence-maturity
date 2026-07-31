# Journal-Neutral Evidence Coding Codebook V1

## 1. Purpose and scope

This codebook governs structured, AI-assisted extraction and named-author
verification of the full-text-verified primary ML-CGS corpus before any
journal-neutral quantitative synthesis is rebuilt. The
unit of analysis is a **paper-level ML-CGS workflow**. If one paper reports two
materially different workflows with different data, validation, and decision
roles, the record must be flagged for author review rather than silently
averaging the workflows.

The codebook is designed around observable full-text evidence. Titles,
abstracts, repository metadata, previous extraction notes, and existing matrix
scores are not sufficient evidence for a positive code. Every positive or
scored judgement must include a page, section, figure, table, or supplement
locator.

Automated extraction may locate candidate passages and generate comparison
workbooks, but it is not a human coder or final scientific adjudicator. Any
recoded value used in manuscript-facing synthesis must either preserve a
separately documented full-text extraction or be verified by a named author
against the full text and a page/section locator. The manuscript does not claim
two-human independent coding or human inter-rater reliability.

## 2. Source and verification rules

1. AI-assisted candidate extraction and A/B comparison files are internal QA
   artifacts. They may identify disagreements but do not establish human
   agreement or final scientific codes.
2. A named author verifies every new manuscript-facing recode against the
   original PDF. Existing full-text extraction may be retained when it remains
   defensible and no WP3 override is applied.
3. Main-text claims, methods, results, supplement, and corrigenda may be used.
   A repository page or abstract alone cannot support a positive full-text code.
4. The PDF locator is mandatory for every positive author-verified finding and
   every author-verified 0-4 score.
5. When distinct workflows cannot be represented by one paper-level code, use
   `unclear` and explain the conflict in the review note.

## 3. Universal evidence states

The following states are not interchangeable.

| State | Operational meaning | Quantitative handling |
|---|---|---|
| `present_explicit` | The full text explicitly reports the item and provides enough detail to classify it. | Eligible for a positive category or score. |
| `confirmed_absent` | The full text explicitly states the item was not used, or the complete methods/validation design makes absence directly demonstrable. | May support score 0 only where the score definition identifies explicit lowest coverage. |
| `not_reported` | The full text does not provide enough information to determine presence or absence. | NA; never score 0. |
| `unclear` | Relevant text exists but is ambiguous, internally inconsistent, or cannot be assigned confidently. | NA; never score 0. |
| `not_applicable` | The item does not logically apply to the workflow or target. | Excluded from the denominator for that field. |

Silence is `not_reported`, not `confirmed_absent`. A random held-out split is not
OOD testing. Use of field-derived inputs is not field validation. Reporting a
posterior or prediction interval is not uncertainty calibration unless its
reliability is evaluated.

## 4. Corpus design for WP3

- **Internal high-risk comparison:** separately generated A/B candidate outputs
  cover all 70 verified primary records for the high-risk fields and five
  maturity dimensions. Their differences are internal QA signals only.
- **Internal full-field comparison:** a deterministic,
  application-stratified 21-record sample (30% of the corpus) was used to test
  the remaining descriptive extraction fields. It is an audit sample, not a
  prevalence estimator.
- **Publication-facing layer:** the locked 70-paper full-text core is retained
  as the baseline. Only named-author, page-level verified overrides may alter
  it. Unverified A/B proposals are excluded from final synthesis.
- The weighted `overall_readiness_score` is retired. WP4 reports the five
  dimensions separately with denominators and missingness.

## 5. High-risk categorical fields

### 5.1 Field validation category

Choose exactly one primary category.

| Code | Definition |
|---|---|
| `operating_storage_site_evaluation` | The ML workflow is evaluated against observations, interpretations, or decisions from an operating or completed geological CO2 storage project. |
| `field_observation_comparison` | The workflow is evaluated against field observations or field interpretations, but not as an operating-site deployment or decision workflow. |
| `field_derived_inputs_only` | Field data, field-derived properties, or a field model are used as inputs/training context without evaluation of ML output against field evidence. |
| `field_inspired_simulation_only` | Geometry or parameters are field inspired, but the evaluation target remains synthetic. |
| `confirmed_absent` | Full text confirms simulation/laboratory-only validation with no field comparison. |
| `not_reported` | Field validation cannot be determined from the full text. |
| `unclear` | The paper uses "field" language but the validation target is ambiguous. |
| `not_applicable` | Field validation is not meaningful for the workflow's stated scope. |

Only the first two categories count as `field_validated`. Field-derived inputs
alone do not.

### 5.2 Controlled-release ML validation

| Code | Definition |
|---|---|
| `ml_evaluated_on_controlled_release` | The ML workflow is directly evaluated using controlled-release observations. |
| `controlled_release_context_only` | Controlled-release evidence is discussed or used as context, but the ML workflow is not evaluated on it. |
| `confirmed_absent` | Full text confirms another validation regime and no controlled release. |
| `not_reported` | No determination is possible. |
| `unclear` | A release experiment is mentioned but its role in ML evaluation is unclear. |
| `not_applicable` | Controlled-release validation is not relevant to the workflow. |

### 5.3 OOD testing category

| Code | Definition |
|---|---|
| `unseen_parameter_range` | Explicit evaluation outside the training parameter range. |
| `unseen_schedule_or_boundary` | Explicit evaluation under unseen well schedules, rates, controls, or boundary conditions. |
| `unseen_geology_or_faults` | Explicit evaluation on unseen geology, facies, connectivity, faults, or structural settings. |
| `multiple_explicit_ood_axes` | Two or more explicit OOD axes are evaluated. |
| `cross_site_heldout` | A site or clearly distinct geological setting is held out from training and used for evaluation. |
| `same_distribution_only` | Full text confirms only random/same-distribution splitting. |
| `confirmed_absent` | The authors explicitly state that OOD/generalization testing was not performed. |
| `not_reported` | The split or distribution shift is not reported sufficiently. |
| `unclear` | The test appears different but the training distribution is not defined. |
| `not_applicable` | OOD testing is not meaningful for the workflow. |

### 5.4 Cross-site testing state

| Code | Definition |
|---|---|
| `explicit_heldout_cross_site_test` | Training and testing are separated across named sites or clearly distinct geological settings. |
| `multiple_sites_no_heldout_test` | Multiple sites are present, but no site-level holdout or transfer evaluation is performed. |
| `single_site_only` | Full text confirms a single-site evaluation. |
| `confirmed_absent` | Authors explicitly identify absence of cross-site testing. |
| `not_reported` | Site structure or transfer design is not reported. |
| `unclear` | Distinct cases may be sites, but the paper does not define them clearly. |
| `not_applicable` | Site-level transfer is not meaningful for the workflow. |

### 5.5 Uncertainty calibration category

| Code | Definition |
|---|---|
| `calibration_or_interval_reliability_test` | Coverage, reliability, calibration error, rank histogram, PIT, or comparable calibration evidence is evaluated. |
| `posterior_predictive_check` | Posterior predictions are checked against held-out or replicated observations. |
| `calibrated_uncertainty_propagated_to_decision` | Calibrated uncertainty is propagated to an optimization, threshold, monitoring, MRV, or corrective-action decision. |
| `uncertainty_reported_not_calibrated` | Ensembles, posterior distributions, variance, or intervals are reported without calibration assessment. |
| `deterministic_or_confirmed_absent` | Full text confirms deterministic treatment or explicitly states no UQ. |
| `not_reported` | Uncertainty treatment cannot be established. |
| `unclear` | Probabilistic language is used but calibration evidence is ambiguous. |
| `not_applicable` | Calibration is not meaningful for the stated output. |

### 5.6 Surrogate-error propagation category

| Code | Definition |
|---|---|
| `propagated_to_posterior_or_inversion` | Surrogate discrepancy is included in likelihood, posterior, inversion, or history-matching uncertainty. |
| `propagated_to_decision_or_optimization` | Surrogate error is propagated to a control, optimization, threshold, or decision metric. |
| `sensitivity_only` | Sensitivity to surrogate error is explored without formal propagation. |
| `error_reported_not_propagated` | Prediction error is reported but downstream inference treats the surrogate as exact. |
| `confirmed_absent` | Full text explicitly confirms no propagation or exact-surrogate treatment. |
| `not_reported` | Downstream propagation cannot be determined. |
| `unclear` | Error terms are mentioned but their propagation role is ambiguous. |
| `not_applicable` | No surrogate is used downstream. |

## 6. Physical diagnostic fields

Code each diagnostic separately using:

`coupled_validation`, `diagnostic_checked`, `encoded_or_simplified`,
`inherited_or_discussed`, `confirmed_absent`, `not_reported`, `unclear`, or
`not_applicable`.

The diagnostic columns are:

- mass conservation;
- pressure threshold or pressure residual;
- plume edge or plume volume;
- geomechanical consistency;
- geochemical/reactive-transport consistency;
- rock-physics consistency;
- sensor/detectability consistency.

`diagnostic_checked` requires a reported test or metric. Merely training on
simulator outputs is `inherited_or_discussed`, not a diagnostic check.

## 7. Maturity score operational definitions

Each score has a companion state: `scored`, `not_reported`, `unclear`, or
`not_applicable`. A numerical value is entered only when the state is `scored`.
Score 0 is a substantive lowest-evidence category; it is never a replacement for
missing information.

### 7.1 Field evidence score

| Score | Observable evidence |
|---:|---|
| 0 | Explicitly synthetic simulation or benchmark only. |
| 1 | Field-inspired simulation, realistic synthetic monitoring, or field-derived inputs without field-output comparison. |
| 2 | Laboratory, controlled experiment, controlled release, or field-derived database comparison below an operating-site case. |
| 3 | Direct evaluation against one field case or operating/experimental storage site. |
| 4 | Multiple field cases or explicit cross-site validation. |

### 7.2 Physical consistency score

| Score | Observable evidence |
|---:|---|
| 0 | Full text confirms no physical check or physical constraint. |
| 1 | Physics inherited from labels or discussed qualitatively. |
| 2 | Simplified constraint, physics loss, or explicit process encoding. |
| 3 | At least one decision-relevant physical diagnostic is quantitatively checked. |
| 4 | Coupled validation across flow and at least one monitoring/risk process. |

### 7.3 Uncertainty score

| Score | Observable evidence |
|---:|---|
| 0 | Explicitly deterministic workflow with no uncertainty treatment. |
| 1 | Sensitivity or uncalibrated ensemble spread. |
| 2 | Probabilistic/Bayesian/posterior uncertainty is reported. |
| 3 | Calibration or posterior predictive reliability is evaluated. |
| 4 | Calibrated uncertainty is propagated into a decision workflow. |

### 7.4 Transferability score

| Score | Observable evidence |
|---:|---|
| 0 | Confirmed same-distribution split only. |
| 1 | Single field-facing case without transfer evaluation. |
| 2 | Unseen parameter range or explicit transfer learning. |
| 3 | Unseen geology, faults, schedules, wells, or boundary conditions. |
| 4 | Explicit held-out cross-site or multiple-field transfer test. |

### 7.5 Decision readiness score

| Score | Observable evidence |
|---:|---|
| 0 | Technical demonstration with no geological-storage decision linkage. |
| 1 | Predicts a storage-relevant variable but does not link it to a decision. |
| 2 | Output is linked to a named storage decision or decision variable. |
| 3 | Workflow is tested near a threshold, alarm, monitoring update, or optimization objective under uncertainty. |
| 4 | Auditable operational/MRV workflow with provenance, documented review path, and demonstrated human or regulatory use. |

## 8. Decision criticality

Decision criticality describes the consequence of the supported decision, not
the popularity or sophistication of the model.

| Score | Decision role |
|---:|---|
| 0 | Background method with no storage decision. |
| 1 | Exploratory screening or triage. |
| 2 | Characterization or non-operational interpretation. |
| 3 | Decision support affecting forecasts, monitoring design, capacity, or risk ranking. |
| 4 | Safety-critical operation, injection control, leakage response, wellbore/seal risk, or MRV-facing assurance. |

The reviewer may use `config/decision_criticality_map.yaml` only after completing
the full-text paper-level judgement. Any override or ambiguity must be explained.

## 9. Full-field sample vocabulary

The 21-record full-field sample additionally codes storage stage, application
area, geological process, decision supported, data regime and source, field
case, scale, dimensionality, ML family/model, baseline, inputs, outputs,
included/omitted physics, uncertainty method, validation type, metrics,
decision metric, main result, main limitation, supported/unsupported claims,
evidence role, and central-claim eligibility.

Use `not_reported`, `unclear`, and `not_applicable` literally. Do not use an empty
cell to encode any of these states. Semicolon-separated values are allowed only
for genuinely multi-label descriptive fields; controlled high-risk categories
remain single choice.

## 10. Evidence role and claim eligibility

Evidence role is separate from maturity.

- `primary_peer_reviewed_journal`: may support a core claim if the coded field
  and full-text locator match the claim.
- `primary_peer_reviewed_preprint_replaced`: use the journal version and record
  the replacement.
- `supplement_only_or_emerging_example`: may illustrate an emerging direction,
  but cannot solely support a central maturity claim.
- `conference_or_expanded_abstract`: cannot solely support central maturity,
  field-readiness, or safety claims.
- `unclear_bibliographic_status`: not eligible for a central claim until
  resolved.

## 11. Internal comparison and author verification

For internal A/B QA, exact agreement and kappa-like comparison statistics may
be calculated to identify unstable fields. These values compare two
AI-assisted candidate outputs; they are not human inter-rater reliability and
must not be reported as such in the manuscript. Report the compared N,
run-specific missingness, and differences involving `not_reported`, `unclear`,
and `not_applicable` states only in internal validation records.

Open-ended full-field descriptions such as application area, data regime,
scale, dimensionality, ML family, and validation type are not nominal
categories merely because they occupy one spreadsheet column. Their exact-text
agreement is only a workload diagnostic. These fields require semantic
full-text review before a new value can enter manuscript-facing synthesis.

No mandatory numerical threshold will be used to conceal disagreement. A field
with unstable candidate extraction must be redefined, retained from the prior
full-text baseline, downgraded to descriptive use, or removed from quantitative
synthesis. The 712 machine-proposed resolutions remain in
`evidence/CODING_ADJUDICATION_LOG.csv` as internal history. Final WP3 changes are
recorded separately in `evidence/WP3_AUTHOR_VERIFIED_OVERRIDES.csv` with the
named reviewer, PDF locator, reason, and claim boundary.

## 12. Completion rule

A manuscript-facing recoded value is complete only when:

1. it has an explicit controlled value;
2. a score has a state and, if `scored`, a 0-4 value;
3. every positive category and score has a page/section locator;
4. the named author, verification date, source PDF, reason, and claim boundary
   are recorded; and
5. the value appears in `evidence/WP3_AUTHOR_VERIFIED_OVERRIDES.csv` or is
   explicitly preserved from the prior full-text baseline.
