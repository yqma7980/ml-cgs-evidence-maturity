# Journal-Neutral Evidence Coding Codebook V2 (WP9.3)

## 1. Purpose

This codebook defines five evidence-maturity dimensions for machine learning in
geological CO2 storage. It is prospective from WP9.3 onward. It clarifies the
boundary among field evidence, physical consistency, uncertainty,
transferability, and decision readiness without changing the locked 70-paper
corpus or the N = 57 main quantitative universe.

The unit of analysis is a paper-level ML-CGS workflow. A paper that contains
materially different workflows must be flagged for author review instead of
being silently averaged. Every positive code or numerical score requires
full-text evidence and a page, section, figure, table, or supplement locator.

The dimensions are complementary evidence layers. They are not interchangeable
measures of a latent property called trustworthiness. No weighted overall
readiness score is permitted.

## 2. Locked evidence roles

Evidence role and evidence maturity are separate decisions.

| Evidence role | Permitted use | Prohibited use |
|---|---|---|
| Verified primary ML-CGS | Quantitative synthesis and primary ML claims within the coded evidence boundary | Claims beyond the extracted full-text evidence |
| Geoscience background | Storage mechanisms, failure pathways, and geological context | Primary ML maturity counts |
| Field anchor | Field-project behaviour and the empirical requirements for validation | Proof of ML field readiness unless the ML workflow itself was evaluated |
| Benchmark-design anchor | Experimental, benchmark, or data-design requirements | Primary ML counts unless explicit evaluated ML is present |
| Review-positioning source | Comparison with prior reviews and scope positioning | Primary-study maturity counts |
| Author synthesis | Framework, interpretation, and research agenda | Presentation as observed empirical evidence |
| Metadata-level candidate | Coverage mapping and acquisition priority | Maturity scores or deployment claims |

## 3. Universal evidence states

Coding begins with an evidence state. A numerical score is considered only
after the state is resolved.

| State | Operational meaning | Quantitative handling |
|---|---|---|
| `present_explicit` | Full text explicitly reports enough evidence to classify the item. | Eligible for a positive category or score. |
| `confirmed_absent` | Full text explicitly states absence, or a complete reported design makes absence directly demonstrable. | May support score 0 only where the score definition names explicit lowest coverage. |
| `not_reported` | The full text does not provide enough information to determine presence or absence. | Missing evidence; never score 0. |
| `unclear` | Relevant text is ambiguous, internally inconsistent, or cannot be classified confidently. | Missing evidence; never score 0. |
| `not_applicable` | The item does not logically apply to the workflow. | Excluded from the denominator for that field. |

Silence is `not_reported`, not `confirmed_absent`. Empty cells are not evidence
states. Unknown, unclear, and not reported are not zero.

## 4. Two-step coding rule

For each dimension, code in this order:

1. identify the observable full-text evidence and record a locator;
2. assign the controlled category;
3. assign a score only if its gate is satisfied;
4. record the score state as `scored`, `not_reported`, `unclear`, or
   `not_applicable`;
5. record the claim boundary, including what the evidence does not support.

Architecture names, author claims, titles, abstracts, and metadata cannot by
themselves satisfy a positive gate. A model may score differently across the
five dimensions. Strong evidence in one dimension cannot compensate for absent
or missing evidence in another.

## 5. Dimension boundaries

### 5.1 Field evidence

**Question:** Against what external empirical setting was the ML output
evaluated?

Field evidence records empirical anchoring of the ML output. Field-derived
inputs, a field-calibrated simulator, named-site geometry, or realistic
synthetic monitoring do not count as field validation unless the ML output is
compared with observations or field interpretations.

Choose one category:

| Code | Definition |
|---|---|
| `operating_storage_site_evaluation` | The ML workflow is evaluated in an operating or completed storage project and is connected to a site workflow or decision. |
| `field_observation_comparison` | The ML output is compared with field observations or interpretations from one field case, without demonstrated operational use. |
| `controlled_field_experiment_evaluation` | The ML output is evaluated using observations from a planned field experiment, controlled injection, or controlled release. |
| `laboratory_or_bench_experiment_evaluation` | The ML output is evaluated using laboratory or bench-scale observations. |
| `field_derived_inputs_only` | Field data, properties, or a field model are inputs or training context, but ML output is not evaluated against field evidence. |
| `field_inspired_simulation_only` | Geometry or parameters are field inspired, but the evaluation target remains synthetic. |
| `confirmed_absent` | Full text confirms simulation-only evaluation with no empirical comparison. |
| `not_reported` | The empirical validation setting cannot be determined. |
| `unclear` | Field language is present, but the role of observations in ML evaluation is ambiguous. |
| `not_applicable` | Field evaluation is not meaningful for the stated workflow. |

Field evidence does not establish transferability. A model evaluated at one
site remains a single-site result unless another site or setting is explicitly
held out.

### 5.2 Physical consistency

**Question:** Which storage-relevant physical relation was encoded or
quantitatively checked?

Code each diagnostic separately using:

`coupled_validation`, `diagnostic_checked`, `encoded_or_simplified`,
`inherited_or_discussed`, `confirmed_absent`, `not_reported`, `unclear`, or
`not_applicable`.

The diagnostic fields are mass conservation, pressure threshold or residual,
plume edge or volume, geomechanical consistency, geochemical or reactive
transport consistency, rock-physics consistency, and sensor or detectability
consistency.

`diagnostic_checked` requires a reported test or metric. Simulator labels imply
physical provenance but do not verify the learned output. A physics loss or
governing-equation residual that is included during training is
`encoded_or_simplified` unless its test behaviour is reported independently.

Physical consistency does not establish decision readiness. A diagnostic
becomes decision evidence only when its error is linked to a named decision
variable, threshold, or action.

### 5.3 Uncertainty

**Question:** Is predictive or inferential uncertainty reported, checked for
reliability, and propagated?

Choose one primary category:

| Code | Definition |
|---|---|
| `calibrated_uncertainty_propagated_to_decision` | Calibrated uncertainty is propagated into optimization, thresholding, monitoring, MRV, or corrective action. |
| `calibration_or_interval_reliability_test` | Coverage, calibration error, reliability, PIT, rank histogram, or comparable evidence is evaluated. |
| `posterior_predictive_check` | Posterior predictions are checked against held-out or replicated observations. |
| `uncertainty_reported_not_calibrated` | A posterior, ensemble, interval, variance, or distribution is reported without a reliability assessment. |
| `sensitivity_only` | Sensitivity or scenario spread is reported without a probabilistic reliability claim. |
| `deterministic_or_confirmed_absent` | The workflow is explicitly deterministic or explicitly omits UQ. |
| `not_reported` | Uncertainty treatment cannot be established. |
| `unclear` | Probabilistic language is present, but the reliability evidence is ambiguous. |
| `not_applicable` | Uncertainty evaluation is not meaningful for the stated output. |

A posterior is not automatically calibrated. Ensemble spread is not a
reliability test. Uncertainty describes confidence conditional on the evaluated
regime; it does not substitute for testing a distribution shift.

Surrogate-error propagation is coded separately as propagation to posterior or
inversion, propagation to a decision, sensitivity only, error reported but not
propagated, confirmed absent, not reported, unclear, or not applicable.

### 5.4 Transferability

**Question:** Was the workflow evaluated outside the distribution represented
in training or development?

Choose one OOD category:

| Code | Definition |
|---|---|
| `unseen_parameter_range` | Evaluation is outside the training parameter range. |
| `unseen_schedule_or_boundary` | Evaluation uses unseen rates, controls, wells, schedules, or boundary conditions. |
| `unseen_geology_or_faults` | Evaluation uses unseen facies, connectivity, geology, faults, or structural settings. |
| `multiple_explicit_ood_axes` | Two or more OOD axes are explicitly evaluated. |
| `cross_site_heldout` | A named site or clearly distinct geological setting is held out from development and used for evaluation. |
| `same_distribution_only` | Full text confirms only random or same-distribution splitting. |
| `confirmed_absent` | Authors explicitly identify absence of OOD or transfer testing. |
| `not_reported` | The training and test distributions are not described sufficiently. |
| `unclear` | Test cases appear different, but the shift is not defined. |
| `not_applicable` | OOD testing is not meaningful for the workflow. |

Cross-site testing is also coded separately:

| Code | Definition |
|---|---|
| `explicit_heldout_cross_site_test` | Training and testing are separated across named sites or clearly distinct geological settings. |
| `multiple_sites_no_heldout_test` | Multiple sites are present, but no site-level holdout is performed. |
| `single_site_only` | Full text confirms one-site evaluation. |
| `confirmed_absent` | Authors explicitly identify absence of cross-site testing. |
| `not_reported` | Site structure is not reported. |
| `unclear` | Distinct cases may be sites, but the paper does not define them clearly. |
| `not_applicable` | Site-level transfer is not meaningful for the workflow. |

A simulated blind test on a new geological setting can establish geological
OOD evidence. It cannot be described as field cross-site validation unless
field observations from a held-out site are used.

### 5.5 Decision readiness

**Question:** What named storage decision can use the output, and what evidence
links the output to an action?

Use the following evidence ladder:

| Level | Observable evidence |
|---|---|
| Technical output | The model predicts or classifies a storage-relevant variable. |
| Named decision linkage | The output is connected to a stated screening, forecasting, control, monitoring, response, or stewardship decision. |
| Evaluated decision mechanism | A threshold, alarm, monitoring update, optimization objective, or action rule is evaluated. |
| Auditable workflow | Provenance, uncertainty, review responsibility, decision logs, and the action path are documented and demonstrated. |

Accuracy on a storage variable is not a decision metric. A statement that a
model may assist operators is not an evaluated decision mechanism. Physical
plausibility and field evaluation remain separate dimensions even when they are
necessary for a decision.

## 6. Score gates

A score is assigned only after the corresponding evidence category is coded.

| Score | Field evidence | Physical consistency | Uncertainty | Transferability | Decision readiness |
|---:|---|---|---|---|---|
| 0 | Explicit synthetic-only evaluation | Explicit absence of physical check or constraint | Explicit deterministic workflow with no UQ | Explicit same-distribution-only evaluation | Technical demonstration with no storage-decision linkage |
| 1 | Field-inspired or field-derived context without ML-output comparison | Physics inherited or discussed | Sensitivity or uncalibrated spread | One field-facing case without transfer evaluation | Storage-relevant output without named decision linkage |
| 2 | Laboratory, controlled experiment, controlled release, or empirical database below an operating-site case | Explicit process encoding, simplified constraint, or physics loss | Probabilistic or posterior uncertainty reported | Unseen parameter range or explicit transfer learning | Output linked to a named storage decision or decision variable |
| 3 | Direct evaluation against one field case or operating/experimental storage site | At least one decision-relevant physical diagnostic is quantitatively checked | Calibration or posterior predictive reliability is evaluated | Unseen geology, faults, schedules, wells, or boundaries | A threshold, alarm, monitoring update, or optimization objective is evaluated |
| 4 | Multiple field cases or explicit cross-site field evaluation | Coupled validation across flow and at least one monitoring or risk process | Calibrated uncertainty is propagated into a decision workflow | Explicit held-out cross-site or multiple-field transfer test | Auditable operational or MRV workflow with documented and demonstrated human or regulatory use |

Score 0 is substantive evidence of the lowest category. Missing information is
not a score. A score that conflicts with its categorical gate is queued for
targeted full-text recheck rather than changed automatically.

## 7. Boundary tests

The operational boundary matrix is stored in
`evidence/WP9_3_DIMENSION_BOUNDARY_MATRIX.csv`. Positive, negative, and
borderline examples for each dimension are stored in
`evidence/WP9_3_BOUNDARY_EXAMPLES.csv`.

The following short tests should be applied before coding:

1. **Field versus transfer:** Was the ML output compared with observations? Was
   the evaluation setting held out from development? These are separate
   questions.
2. **Physics versus decision:** Was a physical relation checked? Was its error
   connected to an action or threshold? A positive answer to the first does not
   imply the second.
3. **Uncertainty versus transfer:** Was confidence reliable in the evaluated
   regime? Was the model tested under a defined shift? Calibration and transfer
   require different evidence.
4. **Prediction versus decision:** Is there a named action rule or objective?
   Predicting a useful variable is not enough for score 3.

## 8. Legacy-value crosswalk

Legacy labels are retained in the R2 source for traceability. They are not
silently mapped to the new vocabulary.

| Legacy value | WP9.3 treatment |
|---|---|
| `controlled_field_evaluation` | Recheck whether evidence is a controlled field experiment, a one-case field comparison, or an operating-site workflow. |
| `field_workflow_evaluation` | Recheck whether the workflow was merely field-facing or demonstrated in an operating storage workflow. |
| `legacy_explicit_ood_test` | Recheck and assign the explicit OOD axis. Do not infer cross-site testing. |
| `legacy_uncertainty_calibration_or_posterior_check` | Recheck whether evidence is calibration, posterior predictive checking, or only posterior reporting. |
| `calibrated_or_posterior_checked` | Recheck only when a future analysis needs separate calibration and posterior-predictive counts. |

The bounded recheck queue is
`validation/WP9_3_AFFECTED_FIELD_RECHECK.csv`. Every row prohibits automatic
writeback.

## 9. Relationship and non-compensation rule

The relationship diagram is stored in
`framework/WP9_3_DIMENSION_RELATIONSHIP.md`. The dimensions answer different
questions:

- field evidence asks where the workflow was empirically evaluated;
- physical consistency asks what storage physics was encoded or checked;
- uncertainty asks how confidence was represented and validated;
- transferability asks whether performance survived a defined shift;
- decision readiness asks what action was evaluated and who can audit it.

No dimension erases missing evidence in another. A physically diagnosed
simulator surrogate can remain untested in the field. A field comparison can
remain uncalibrated. A calibrated model can fail under geological shift. A
transfer test can lack a decision mechanism.

## 10. Verification and writeback

Automated rules may detect a boundary conflict and prepare a recheck queue.
They cannot resolve the scientific code. Any manuscript-facing change requires:

1. a named author;
2. the original full text;
3. a page or section locator;
4. the previous value and the proposed value;
5. a reason tied to this codebook;
6. a claim boundary; and
7. an explicit author decision to retain, revise, downgrade, or exclude the
   field from synthesis.

No majority rule is used. Blank, `not_reported`, and `unclear` values are never
converted to zero. Until the targeted queue is closed, current quantitative
outputs remain frozen and WP9.3 definitions are used prospectively for WP9.4.
