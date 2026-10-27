# Search history addendum, 23 October 2026

This addendum supports revised Methods 2.2 and Supplement Tables S10c--S10i. It is included in public data/code version v2.3.0-data-code-addenda-20261027. The prior v2.2.0 record remains unchanged and does not contain this addendum.

## Read in this order

1. `TableS10c_EARLY_QUERIES.csv`: 43 actual Crossref queries in 13 topics, with requested limit 15. Batch execution is supported; complete per-query responses are not available.
2. `TableS10c2_PRIORITIZATION_QUOTAS.csv` and `historical_scripts/select_esr_core_literature.py`: quotas, citation/title ranking, penalties and exact weights. Programmatic prioritization is not independent human screening.
3. `TableS10d_EXECUTION_EVIDENCE.csv`: research-relevant summaries of retained historical execution events, source line numbers, event IDs and payload hashes. These are not a complete independently authenticated parent-session log. The private transcripts are not redistributed.
4. `TableS10e_HISTORICAL_STAGES.csv` and `stage_crosswalks/`: distinct 31/469/439/176/177/173/61/70/74/42 stages and bounded relationships. In particular, the rerun requested Crossref again: 469 minus 439 is not a verified 30-record exclusion set.
5. `TableS10f_JULY_BATCH_SETTINGS_AND_COUNTS.csv`: three main query strings, all four configured providers, `-n 8`, `-y 2026` and saved counts. The invocation arguments were `paper-search search "<query>" -n 8 -s crossref,openalex,semantic,arxiv -y 2026`. This is a transcription, not a new execution.
6. `TableS10g_JULY_RETURNED_RECORD_YEARS.csv` and `saved_normalized_retrieval_outputs/`: 42 distinct DOIs; 27 saved metadata dates in 2025--2026, 15 earlier, total range 2008--2026. The range is not a prespecified review window. These JSONs are normalized workflow outputs, not complete provider raw responses. Zero saved provider rows do not diagnose an API failure.
7. `TableS10h_SCREENING_STAGE_STATES.csv`: 74 legacy and 42 update records with separate initial/later statuses, stable IDs and reasons. The update changes from query-stage three primary plus two excluded for insufficient detail to five primary after acquisition; S10b supplies the date/DOI bridge. This does not imply every historical screening action is recoverable.
8. `TableS10i_QUERY_STREAM_BOUNDARIES.csv`: early retrieval, title lookup, separate July trial, main July update, later coverage check and publication-identity audit are not interchangeable batches.

## Preserved originals versus current interpretation

The source-to-public checksum ledger is `../release_notes/SOURCE_TO_PUBLIC_MANIFEST.csv`. It distinguishes unchanged documentary copies from public projections. In the three saved normalized outputs, provider abstracts and opaque ancillary `extra` fields are omitted; query parameters, source counts, bibliographic fields, order and record multiplicities remain unchanged. These public projections are not complete provider responses or byte-identical original retrieval files. Historical planning text such as `2025-2026`, `raw`, or old screening labels is retained as evidence of that earlier document, not adopted as a verified description of all actual retrieval behavior.

The new S10c--S10i CSVs are documentary summaries/read-only projections with a 23 October 2026 interpretation. They do not overwrite original logs or imply that current tool implementations certify historical runtime filtering. The complete historical per-query returns and screening trail remain incomplete.

The original S10 log is `../historical/TableS10_update_search_log.csv`; the acquisition/DOI bridge is `../current_R2/TableS10b_query_to_acquisition_time_bridge_R2.csv`. Current scientific tables remain in `../current/`. No inference should be drawn from an old inventory count to current membership without its separate source-bound member table.

## Scope and use

The 68/23 membership, seven indicators, score distributions, S16 and historical 627-item comparison are unchanged. The retained scripts contain historical paths and network requests: do not run them as a reproduction step. This task did not execute them or perform new retrieval. No copyrighted full-text library, private approval record, credentials or unredacted session transcript is included in this addendum.


Package integrity is recorded by the root `MANIFEST_SHA256.csv`. Historical script copies are documentary evidence; do not rerun their network or output-writing defaults.
