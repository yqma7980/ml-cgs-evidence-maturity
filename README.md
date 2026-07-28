# ML-CGS evidence maturity review data and scripts

This release accompanies the Review Article **The evidence gap, not the algorithm gap: trustworthy machine learning for geological CO2 storage**.

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
papers are included. None of the 712 machine-proposed WP3 resolutions is used.

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
