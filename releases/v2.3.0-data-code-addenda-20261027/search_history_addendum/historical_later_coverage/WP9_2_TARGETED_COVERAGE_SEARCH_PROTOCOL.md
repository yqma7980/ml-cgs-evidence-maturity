# WP9.2 Targeted Coverage Search Protocol

## Date and purpose

- Search date: 2026-08-01
- Purpose: bounded coverage mapping for WP9.2, not corpus expansion and not an exhaustive systematic update.
- Quantitative source of truth: the locked 70-paper corpus and the unchanged 57-paper main quantitative universe.

## Sources

- publisher and DOI landing pages;
- Crossref or other official bibliographic metadata;
- legal open full text or author manuscripts when identified;
- arXiv only for records classified as emerging directions or precursors.

## Concept blocks

The geological-storage block combined geological CO2 storage, sequestration, saline aquifer, depleted reservoir, offshore storage, faulted reservoir, and EOR-storage terms with:

1. physics-informed, PINN, or physics-guided ML;
2. neural operator, FNO, U-FNO, or wavelet operator;
3. multimodal, data fusion, or multiphysics monitoring;
4. digital twin or digital shadow;
5. generative, GAN, diffusion, or Brownian bridge;
6. reinforcement learning, closed-loop control, or policy optimization;
7. foundation model or large language model.

## Classification rules

- `already_in_verified_core`: existing locked evidence; no new count.
- `background_or_review_positioning`: useful context without verified primary ML evidence.
- `candidate_full_text_verification`: potentially in scope, but excluded from claims until legal full-text extraction and classification.
- `emerging_direction_only`: preprint or insufficiently established record used only to map direction.
- `out_of_scope`: no storage-relevant evaluated ML.
- `duplicate_or_precursor`: duplicate, preprint precursor, or non-independent record.

Metadata and abstracts do not support maturity scores. Unknown or unstratified coverage is not converted to zero.

## Limits

This update was intentionally bounded. It records method and geological-context gaps that may warrant a later controlled corpus update. It does not estimate global literature prevalence and does not alter any locked manuscript result.
