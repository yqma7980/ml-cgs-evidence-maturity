# Competing-review delta codebook

## Purpose

This codebook supports WP1 of the journal-neutral novelty rewrite. It records observable features of recent reviews without treating silence in an abstract or publisher page as confirmed absence.

## Comparison set

- `direct`: a review centered on machine learning for geological CO2 storage.
- `near_direct`: a review with substantial overlap in computational storage, monitoring, decision support, or deployment.
- `contextual`: a non-ML review used to define field, leakage, monitoring, or Earth-science validation expectations.

The WP1 exit gate is evaluated primarily against `direct` and `near_direct` reviews. Contextual reviews prevent the new manuscript from claiming novelty for established Earth-science concepts.

## Verification levels

- `full_text_and_supplement`: full article and relevant supplementary material inspected.
- `full_text`: full article inspected.
- `publisher_page_and_abstract`: publisher metadata and abstract inspected.
- `official_abstract`: an official indexing or repository abstract inspected.
- `publisher_metadata`: bibliographic metadata inspected; feature coding is necessarily limited.

## Feature codes

- `yes`: the inspected source explicitly contains the feature.
- `partial`: the feature is present, but narrower, less operational, or less traceable than the WP1 definition.
- `no`: the inspected full text explicitly establishes absence. This value must not be inferred from silence.
- `unclear`: the inspected material does not support a reliable yes/no decision.
- `not_applicable`: the feature is outside the review's stated purpose.

## Coded features

| Field | Observable criterion |
|---|---|
| `search_transparency` | Databases, date boundary, search terms, screening logic, and corpus flow are reported sufficiently for repetition. |
| `corpus_verification` | Included primary studies are individually verified and their evidence role is distinguished from background sources. |
| `decision_framing` | Evidence is organized around storage decisions and decision variables rather than only methods or application categories. |
| `physical_diagnostics` | The review evaluates explicit checks such as conservation, pressure thresholds, plume volume, coupled-process consistency, rock physics, or detectability. |
| `uncertainty_calibration` | Calibration, interval reliability, posterior predictive checking, or decision propagation is evaluated, not merely uncertainty mentioned. |
| `transfer_testing` | OOD, cross-geology, cross-site, boundary-condition, or schedule-shift testing is evaluated explicitly. |
| `field_validation` | ML workflows are evaluated against field observations, field interpretations, operating-site evidence, or controlled-release evidence. Field context alone is insufficient. |
| `mrv_auditability` | Provenance, monitoring updates, versioned decisions, thresholds, human review, and audit trails are treated as components of MRV-facing use. |
| `open_traceability` | Public data link study-level coding to quantitative conclusions. A narrative bibliography alone is insufficient. |
| `sim_to_real_or_deployment_roadmap` | A stated roadmap addresses movement from simulation or benchmark evidence toward field deployment. |

## Coding rules

1. Silence is coded `unclear`, not `no`.
2. A review that discusses uncertainty is not automatically coded as uncertainty calibration.
3. A review that cites field projects is not automatically coded as field validation of ML.
4. A public list of included studies is `partial` open traceability unless the extracted fields behind quantitative conclusions are also released.
5. GitHub and Zenodo outputs planned for the present review remain `planned` until a public URL and immutable release are available.
6. The matrix is a positioning audit, not a quality ranking of competing reviews.

## Freeze

- Search and coding freeze: 2026-07-27.
- Scope: reviews known to the project and targeted verification of recent direct or near-direct competitors.
- The matrix must be refreshed immediately before journal submission.
