# ML-CGS evidence maturity review data and scripts

## Current data and code: v2.3.0

This repository supports **From simulator emulation to storage decisions: A decision-centered review of evidence maturity in machine learning for geological CO2 storage** (JGGC-D-26-00771).

Current release: `v2.3.0-data-code-addenda-20261027`, published 27 October 2026.

- [Organized version directory](releases/v2.3.0-data-code-addenda-20261027/)
- [Download the release ZIP and SHA-256 checksum](https://github.com/yqma7980/ml-cgs-evidence-maturity/releases/tag/v2.3.0-data-code-addenda-20261027)
- [Zenodo version DOI: 10.5281/zenodo.23689746](https://doi.org/10.5281/zenodo.23689746)
- [Current coding manual](releases/v2.3.0-data-code-addenda-20261027/coding_manual/CURRENT_CODEBOOK_ENTRY.md)

The version directory separates current tables, coding rules, frozen inputs, replay code, recovered search records, editorial clarifications, and explicitly historical tables. Use its README and manifests rather than combining files from different release directories.

## Scientific scope

The main analysis contains 68 evaluated-document units; the selected verified-journal sensitivity subset contains 23. Seven primary positive counts are 9/5/14/1/12/4/30, with effective denominators 66/61/61/61/55/26/31. Missing, unclear, unknown and not-applicable states are not zero scores. These findings describe a purposive corpus, not field-wide prevalence.

The historical 57-record comparison remains 627 items: 139 exact agreements, 450 adjudicated disagreements and 38 without a locked baseline. Its human-review coverage is not expanded to the current corpus.

This release adds the recovered S10c-S10i search-history material, S28a/S28b evidence-interface tables and the previously documented FA014 annotation-only correction. It does not change scientific classifications, scores, memberships or result counts. Two isolated local replays matched all 58 frozen scientific reference CSVs; this is not a new coding round or cross-machine validation.

## Reproduction and access

Follow the [version-specific replay instructions](releases/v2.3.0-data-code-addenda-20261027/README.md#reproduce-the-bounded-derived-tables). The bounded replay uses Python 3.11+ and its standard library. Write outputs to a new directory outside the archive. Historical network-retrieval scripts are retained as documentation, not instructions to rerun historical searches.

This is a data/code archive, not a manuscript preprint. Manuscripts, response and cover letters, private author chats and approvals, copyrighted full texts and credentials are excluded. Public projections omit private administrative fields and provider abstracts; the transformation and omission ledgers identify these changes. The original local sources are preserved.

Data and author-created documentation retain CC BY 4.0; author code retains MIT. Bibliographic metadata do not confer rights to the underlying publications. See the version-specific license notices and `CITATION.cff`.

## Preserved historical releases

- [v2.2.0 frozen68/strict23 directory](releases/v2.2.0-frozen68-strict23-20261007/) and [Zenodo DOI 10.5281/zenodo.23336095](https://doi.org/10.5281/zenodo.23336095).
- [Earlier Zenodo archive, DOI 10.5281/zenodo.21644711](https://doi.org/10.5281/zenodo.21644711).

The older root `data/`, `scripts/` and `docs/` directories and prior tags are retained for provenance. They include earlier 70-record inventories and 57-record analysis views and are not the current 68-unit result set. Earlier manuscript titles in those records are historical. Use the current version directory for present results and the historical directories only for explicitly identified comparisons.
