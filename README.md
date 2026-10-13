# ML-CGS evidence maturity review data and scripts

## Current revised data and code

The current revision supports **From simulator emulation to storage decisions:
A decision-centered review of evidence maturity in machine learning for
geological CO2 storage**.

Version: `v2.2.0-frozen68-strict23-20261007` (scientific snapshot frozen on
2026-10-06; data/code publication prepared on 2026-10-13).

- [Versioned data, coding manual, schemas, provenance, and replay code](releases/v2.2.0-frozen68-strict23-20261007/).
- Main analysis: 68 evaluated-document units; strict journal sensitivity: 23.
- Seven positives: 9/5/14/1/12/4/30; available denominators: 66/61/61/61/55/26/31.
- Missing, unclear, and inapplicable values are not treated as zero.
- Two earlier local replay checks matched 58 frozen scientific CSVs. This does
  not establish independent source recoding, cross-machine validation, or model
  deployment readiness.
- Data/documentation: CC BY 4.0; replay code: MIT. Operative notices and citation
  metadata are inside the versioned directory.

This is a data/code release, not a manuscript or preprint. Copyrighted full texts,
manuscript files, peer reviews, private approvals, correspondence, and credentials
are excluded. The new Zenodo deposit is pending login and has **no verified DOI
yet**. The historical DOIs below do not identify this revision.

## Historical archive information

The sections below describe the older archive accompanying **The evidence gap,
not the algorithm gap: trustworthy machine learning for geological CO2 storage**.
They are preserved for provenance, not used as the current 68/23 revision.

## Contents

- `data/`: sanitized paper-level coding, derived evidence profiles, aggregate plot data,
  field-anchor roles, and figure/table traceability.
- `scripts/`: deterministic Python and PowerShell scripts used to regenerate and validate
  the IJGGC figures and tables from the locked evidence files.
- `docs/`: data dictionary and release notes.

## Evidence boundaries

The frozen full-text verified primary corpus contains 70 records. The main quantitative
universe contains 57 claim-eligible records. Missing, unclear, and not-reported values are
retained and are not interpreted as zero. Exactly six author-verified overrides across four
papers are included.

This public release excludes copyrighted full-text PDFs, extracted quotations, page notes,
local paths, signatures, private correspondence, and human-adjudication workbooks.

## Reproduction

Install Python 3.11 or later and the packages in `requirements.txt`, place this release in the
project layout described in the scripts, and run `scripts/run_wp8_ijggc_figures_tables.ps1`.
The archived CSV files also permit independent reanalysis without the manuscript source.

## Citation

Use the citation in `CITATION.cff`. The versioned archive is available from
[Zenodo](https://doi.org/10.5281/zenodo.21644711), and the public repository is
[GitHub](https://github.com/yqma7980/ml-cgs-evidence-maturity).

## Licenses

Code is released under the MIT License. Review-derived data and documentation are released
under CC BY 4.0. Bibliographic metadata remain subject to their source terms.
