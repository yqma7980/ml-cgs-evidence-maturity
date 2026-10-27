# M004 review evidence data and replay code

Version `v2.3.0-data-code-addenda-20261027` | 27 October 2026 | DOI: https://doi.org/10.5281/zenodo.23689746

This archive supports *From simulator emulation to storage decisions: A decision-centered review of evidence maturity in machine learning for geological CO2 storage* (JGGC-D-26-00771). It contains review-derived scientific data and code, not the manuscript or peer-review correspondence. The version DOI is registered on Zenodo publication, not merely on reservation.

## Start here

| Directory | Contents and authority |
| --- | --- |
| `current/` | Current 68-unit analysis, selected 23-unit journal sensitivity subset, indicators, member lists, scores, mappings, S9 and S16 tables. |
| `coding_manual/` | Current definitions, adopted physical-diagnostic criteria, V2 rubric and boundary examples. Start with `CURRENT_CODEBOOK_ENTRY.md`. |
| `FINAL_SCIENCE_SNAPSHOT/` | Frozen scientific input and historical 627-item comparison. |
| `portable_replay/` | Same scientific inputs, deterministic Python script and reference outputs for the bounded 58-table replay. |
| `search_history_addendum/` | S10c-S10i, 43 early queries, historical batch evidence, July parameters/outputs and bounded screening crosswalks. |
| `editorial_clarifications/` | S28a physical-score/union correspondence, S28b field/anchor coverage and FA014 annotation erratum. |
| `current_R2/`, `historical/` | Explicitly historical/intermediate tables, not alternative current results or pending author decisions. S25/S26 remain under their cited `current_R2/` paths. |
| `release_notes/` | Public transformation ledger, omission rationale, applied annotation corrections, manifest and actual replay checks. |

## Stable scientific results

The primary analysis has 68 evaluated-document units; the selected verified-journal sensitivity subset has 23. Primary positive counts are 9, 5, 14, 1, 12, 4, 30; available denominators are 66, 61, 61, 61, 55, 26, 31. Missing, unclear, unknown and not-applicable states are not zero scores. A recorded test may have an adverse result. These are purposive-corpus findings, not estimates of field-wide prevalence.

The historical comparison remains 57 records x 11 fields = 627 items: 139 exact agreements, 450 adjudicated disagreements and 38 without a locked baseline. It is not expanded to the current 68 units. Historical filenames containing `independent_review` do not establish blinding or two independent initial human coders. Liu's separately bound GHGT unit does not establish equivalence to the registered journal object and is not admitted to the strict journal subset on that basis.

## What this version adds

The prior v2.2.0 public record remains at https://doi.org/10.5281/zenodo.23336095. This version includes the recovered search addendum, complete current coding-manual entry and additional evidence-interface tables. It applies the previously documented FA014 **annotation-only** erratum to current public relationship copies. The bounded reservoir-characterization role, 32-relation inventory, all scientific classifications, scores, memberships and result counts are unchanged. Historical annotations remain historical evidence.

Private author messages, approval forms/signatures, local-machine paths, manuscripts, response/cover letters, full-text literature and credentials are excluded. Two excerpt columns and the `abstract`/opaque `extra` fields in three saved retrieval JSONs are omitted from public copies; all retained bibliographic fields and record order are unchanged. Public copies must not be mistaken for byte-identical private source files: `release_notes/SOURCE_TO_PUBLIC_MANIFEST.csv` records both checksums and `PUBLIC_OMISSIONS.csv` identifies projections. Original local files were preserved.

## Reproduce the bounded derived tables

Python 3.11+ and its standard library suffice. From this directory, choose NEW output directories outside the archive:

```sh
python portable_replay/scripts/replay_frozen_snapshot.py --replay-only --output ../m004_replay_output
python verify_replay_outputs.py --output ../m004_replay_output
```

The verifier compares all 58 generated CSVs with their complete reference rows and columns. The delivered `release_notes/REPLAY_VERIFICATION.json` records actual local checks. This is computation on frozen inputs, not independent recoding, new literature retrieval, new simulation or cross-machine validation. Historical search programs are documentary copies; do not run their network/output defaults. Main-text/SI PDFs and graphical manuscript source are intentionally outside this data/code archive; the replay does not claim to rebuild them.

## Versions, access and licensing

GitHub version folder: https://github.com/yqma7980/ml-cgs-evidence-maturity/tree/v2.3.0-data-code-addenda-20261027/releases/v2.3.0-data-code-addenda-20261027

GitHub release: https://github.com/yqma7980/ml-cgs-evidence-maturity/releases/tag/v2.3.0-data-code-addenda-20261027

Current Zenodo version: https://doi.org/10.5281/zenodo.23689746

Data and author-created documentation: CC BY 4.0. Author code: MIT. Bibliographic facts identify third-party works but confer no license to the underlying publications. See `LICENSE-DATA.txt`, `LICENSE-CODE.txt` and `CITATION.cff`. The canonical folder layout is retained here; any separate short-filename journal adapter is not the repository layout.
