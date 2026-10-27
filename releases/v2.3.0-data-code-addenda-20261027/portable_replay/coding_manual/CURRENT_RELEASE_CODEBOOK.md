# Current release coding guide

The current unit input is ../FINAL_SCIENCE_SNAPSHOT/FINAL_SCIENCE_SNAPSHOT.csv. Use the exact DERIVATION_RULES_FROZEN.json in that folder. The main scope is 68; the strict journal subset is 23. CODEBOOK_V2.md is retained byte-exactly as a historical definition document, not as a current denominator. Its historical example/recheck-queue links are not bundled and do not reopen decisions.

## Evidence states and numerical handling

An explicit reported design may support a substantive low score, including 0. Silence, ambiguity, an inapplicable item or incomplete extraction cannot be assigned 0. `not_reported`, `unclear`, `not_applicable` and `unknown` are distinct states; scores are blank when the state is not `scored`. Current primary-analysis outputs have no unresolved `unknown` or review-pending category. This is an output condition, not a license to force a missing input into another state.

For indicators, `Available` includes positive and classifiable non-positive cases only. NR, U and NA remain separate. Non-positive does not necessarily mean a test failed. Test implementation and test outcome must be distinguished: a poor unseen-well result can still document an OOD test.

## Retained 0-4 rubric

The complete dimension-specific gates remain in V2 Sections 5-6. This table reproduces their levels as a reading aid; the physical column is interpreted with the approved clarification below.

| Score | Field evidence | Physical consistency | Uncertainty | Transferability | Decision readiness |
|---|---|---|---|---|---|
| 0 | Explicit synthetic-only evaluation | Explicit absence of a physical check or constraint | Explicit deterministic workflow without UQ | Explicit same-distribution-only evaluation | Technical demonstration without storage-decision linkage |
| 1 | Field-derived inputs or field-inspired setting, without output comparison | Physics inherited or discussed | Sensitivity or uncalibrated spread | One field-facing case without transfer evaluation | Storage-relevant output without named decision linkage |
| 2 | Laboratory, controlled experiment or empirical database evaluation | Explicit process encoding, simplified constraints or physics loss | Probabilistic or posterior uncertainty is reported | Unseen parameter range or explicit transfer-learning evaluation | Output is linked to a named decision or variable |
| 3 | Direct output evaluation against a field case | At least one decision-relevant quantitative physical diagnostic | Calibration or posterior predictive reliability is evaluated | Unseen geology, faults, schedules, wells or boundaries | A threshold, alarm, update or optimization objective is evaluated |
| 4 | Multiple field cases or explicit cross-site field evaluation | Finite coupled validation across flow and a monitoring/risk process | Calibrated uncertainty is propagated into a decision workflow | Explicit held-out cross-site or multiple-field transfer test | Auditable operational/MRV workflow with demonstrated human or regulatory use |

These dimensions are not a weighted total and do not compensate for one another. The score table is not a substitute for a documented category, locator and decision.

## Adopted physical-diagnostic rules

Separate physical information encoded or inherited by the model from quantitative checks of learned or hybrid-workflow outputs. A diagnostic needs an identified object, physical relation or decision-relevant quantity, quantitative criterion, reference, evaluation conditions and source locator. Governing equations, simulator labels, a training loss or a general RMSE/SNR alone do not automatically establish such a diagnostic. Synthetic or numerical references are permitted when appropriate to the object evaluated.

Convergence of the same training, assimilation or inverse-fit objective is not by itself independent validation. A separate physical re-evaluation, held-out observation or explicit observation/noise-scale check is assessed according to its actual object and purpose. Residual checks are not categorically excluded. Their relation to the fit data must be recorded.

The finite-coupling level retains V2's meaning: the evaluated workflow needs an explicit reference, quantitative result and traceable coupling path across flow and a monitoring/risk process. Bidirectional coupling is not universally required. Multiple inputs, outputs or a THM label do not automatically establish score 4.

A diagnostic can reveal a bias or failure. That still records an implemented check; it does not imply that the model passed or earned a high score.

The physical indicator is the union of seven prespecified components: mass conservation, pressure threshold/residual, plume edge/volume, geomechanics, geochemistry, rock physics and sensor physics. Checks outside those components are recorded separately, not squeezed into a wrong component or called absent. The union is not an exhaustive count of physical validation. Physical scores and this union need not be equal.


## Source/version limits

Use data/TableS09_FINAL.csv, TableS09a_FINAL.csv, the Wen field/source tables and docs/WEN_SOURCE_PROVENANCE_README.md. Current adopted boundary examples are included locally. The accompanying tables document the retained classifications, source versions and historical comparisons.
