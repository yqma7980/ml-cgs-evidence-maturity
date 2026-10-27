# Search Strategy V1

## Scope and purpose

WP2 closes the existing metadata-level candidate pool and performs a bounded post-freeze search update for primary machine-learning evidence in geological CO2 storage. This is an evidence-map screening workflow, not a statistical meta-analysis.

## Evidence streams

1. **Legacy candidate pool.** The 74 records in `evidence/METADATA_LEVEL_RECORDS_TO_VERIFY.csv` at the WP2 baseline were screened against the project scope and classified once. Their provenance is the curated evidence matrix assembled before the journal-neutral rewrite. WP2 does not reconstruct undocumented historical query syntax; this limitation is retained explicitly.
2. **Targeted update.** A small, bounded search was run on 2026-07-27 to identify recent or missed studies relevant to storage dynamics, monitoring/history matching/MRV, leakage, wellbore, geomechanics, and seal risk.

## Targeted queries

- `geological carbon storage machine learning pressure plume surrogate neural operator 2026`
- `geological CO2 storage machine learning monitoring history matching data assimilation MRV 2026`
- `geological CO2 storage machine learning leakage wellbore geomechanics seal risk 2026`

## Sources and limits

- Sources queried through the local paper-search workflow: Crossref, OpenAlex, Semantic Scholar, and arXiv.
- Last search date: 2026-07-27.
- Requested publication window: 2025-2026, with 2026 emphasized. Older API returns were retained only when needed to identify duplicates, precursors, or background anchors.
- Language: English-language title/abstract metadata and accessible English full text.
- Result cap: eight results per source/query in the bounded update; no unbounded acquisition sprint was run.
- Legal access only: publisher-open PDFs, repository manuscripts, and locally supplied lawful copies. Paywall bypassing and pirate sources were prohibited.
- API limitations: two Semantic Scholar calls returned rate-limit errors; CORE/DOAJ credentials and an Unpaywall email were not available. These limitations are reported rather than silently replaced with inferred evidence.

## Deduplication

Records were normalized by DOI first, then checked by title and publication lineage. Preprints and conference precursors were linked to verified journal versions where identifiable. A duplicate or precursor does not increase corpus counts.

## Eligibility

A primary record must contain an explicit ML or data-driven workflow applied to geological CO2 storage and sufficient full-text method, data, validation, and limitation detail. Reviews, non-ML field studies, mechanism papers, conference abstracts without extractable detail, and out-of-scope capture/EOR/natural-gas-storage studies do not enter the primary quantitative synthesis.

## Screening states

- `added_verified_primary`
- `background_anchor`
- `excluded_out_of_scope` or `excluded_insufficient_detail`
- `duplicate_or_precursor`
- `supplement_only`
- `eligible_full_text_pending`

Unknown, unclear, not reported, and confirmed absence remain distinct. Missing full text is not scored as zero and is not treated as evidence against a method.

## Reproducibility files

- Raw search records: `validation/search_update_raw/`
- Legacy decisions: `config/wp2_pending_status_map.csv`
- Update decisions: `config/wp2_targeted_search_status_map.csv`
- Closed legacy ledger: `evidence/SCREENING_DECISIONS_V1.csv`
- Targeted update ledger: `evidence/SEARCH_UPDATE_DECISIONS_V1.csv`
