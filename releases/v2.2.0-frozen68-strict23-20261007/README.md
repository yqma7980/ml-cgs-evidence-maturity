# M004 revised evidence data and replay code

Public-deposit preparation authorized by the user on 2026-10-13. This is a data/code archive, not a manuscript or preprint. Actual repository publication and DOI registration are verified separately; no reserved DOI is presented as a published record.

## Version and snapshot binding

Version/tag: `v2.2.0-frozen68-strict23-20261007` (frozen science date 2026-10-07).
Science: `STAGE18_FINAL_SCIENCE_SNAPSHOT_20261006`. Source package: `TARGETED_FINAL_CORRECTION_20261007_004819`.
Original private-complete snapshot SHA-256: `a82232024ef32fcb06e9aeecf0c45b1d72a034f6516c487d36f968fa74f9465f`.
Curated snapshot SHA-256: `452fbc36e2228ba9c80ddea8f0b93a38e370d843e696f0affc2fc94b7074cccd`.
Protected scientific projection SHA-256: `5459ec60ae476a9b0ad5e298a6aad56fcff026784e21cfa798c4409fe7ce33a1`.
Scientific values, raw missing states, memberships, mappings, row order and all
selected provenance strings are retained exactly. Private and unused legacy/
noncanonical staging columns are removed; all adopted replay-required science
columns are retained. The 134 omitted snapshot columns are listed explicitly;
therefore curated input hashes differ. No originals have been modified. See the
exact source/file/field bindings and TRANSFORMATIONS.json, not filename alone.

## Contents and evidence units

- FINAL_SCIENCE_SNAPSHOT/: 71 evaluated-version/inventory rows (68 active, 3
  non-primary), exact frozen rules, anonymous 627-item historical inputs and the
  Liu evaluated-document identity. Seventy inventory IDs are not 71 independent
  studies. Liu's registered CORE lineage is retained outside the main analysis;
  only its SHA-bound GHGT document contributes, and never to the strict subset.
- data/: original frozen numerical/member outputs, full seven-indicator states,
  five scores and score states, all ten joint pairs in both scopes with missing
  margins, decision/method mappings, complete membership incl. HOLD/EXCLUDE,
  32 source-site/project relations and field-specific Wen source provenance.
- coding_manual/: historical V2 rubric (its 70/57 statements are HISTORICAL),
  current operational guide and adopted examples including adverse/missing cases.
- schema/: every CSV's exact columns/row counts and the explicit privacy projection.
- docs/: source hashes, transformation ledger, coverage, exclusions, license
  evidence and reproduction boundaries. Source PDFs themselves are NOT included.
- scripts/: replay-only code extracted from the own derivation script. Private
  freeze/approval/production routes are absent. Originally syntax checked only;
  two subsequent local replay runs matched all 58 scientific reference CSVs.
  See docs/CURRENT_COMPLETENESS_AND_RUNTIME_CHECK.md and CURRENT_RUNTIME_CHECK.json.

Main units 68; strict journal sensitivity 23. Seven positives in frozen metric
order: 9/5/14/1/12/4/30; corresponding Available: 66/61/61/61/55/26/31. Exact
metric names and all NON_POSITIVE/NR/U/NA values remain in the summary and member
tables. Non-positive is not automatically a failed test. Missing/unclear/NA are
not zero. An implemented adverse test remains a test, not a demonstrated pass.
Physical diagnostic implementation and physical maturity scores are distinct.

The historical comparison stays 57 records/627 items; 55 current units overlap
and 13 lack original A/B coverage. This does not assert new independent human
recoding. Relation rows are not independent studies/sites/events. Event-unit
blanks remain missing and are not completed. Pair-effective denominators and
missing margins must be used rather than treating 68/23 as every pair's N.

Wen's 54 field-source entries retain 16 prior formal-source addenda and 38 retained
base-context entries. Source hashes/locators are field-specific, not a blanket
final-journal bridge. Neither Wen record is promoted to strict sensitivity.
Liu GHGT does not inherit registered-journal values or strict membership.
DOI/title fields identify literature sources only, not a DOI for this archive.

## Integrity, reproduction and limitations

MANIFEST_SHA256.csv contains every payload file EXCEPT itself. It has no circular
self-hash. ZIP SHA-256 is supplied separately in the local delivery/QA, not
inside itself. Verify member sizes/hashes and ZIP CRC when downloading this release.

No science computation was executed during the original candidate preparation.
The later packaging-closure check ran the existing frozen replay twice in
separate output directories; all 58 scientific reference CSVs matched, and
both runs had identical scientific CSV hashes. No scientific values changed.
Most archived derived
outputs are byte-identical copies. Private-bearing membership/history/Wen tables
are exact retained-column projections. Replay's scientific rule/count/score
body is retained; only packaging, paths, history-projection hash binding and
integrity-metadata naming change. See docs/REPRODUCTION_SCOPE.md for the original
scope record and docs/CURRENT_COMPLETENESS_AND_RUNTIME_CHECK.md for the later
actual runtime check. Use a separate output folder; local computational parity
does not establish source validity, cross-machine reproduction or journal
compliance closure.

This is a bounded review-coded evidence dataset, not new laboratory, field or
simulation data, not exhaustive literature coverage or evidence of deployment
readiness. Version equivalence, independence, missing search history and
source-specific limits remain explicit. Review/article PDFs, long extracted
quotations, manuscript sources/peer reviews/letters, approvals/returns/sheets,
personal communication, credentials and unrelated project material are excluded.
Only metadata identifying source documents are retained.

## Licenses and citation

Data and documentation: CC BY 4.0 (LICENSE-DATA.txt).
Code in scripts/: MIT (LICENSE-CODE.txt).
See CITATION.cff for the seven authors and version identity. The repository is
https://github.com/yqma7980/ml-cgs-evidence-maturity.

The historical directory releases/v2.1.0-wp9-8-r1 and Zenodo record 21753851
identify older materials, not this 68/23 revision. The historical concept DOI
is not a substitute for a new version-specific DOI. Consult the current
repository release for the verified new archive link once deposit completes.

## Portable replay

Python 3.11 or later; the replay script uses only the standard library.
Run from this extracted archive, using a separate output directory:

```text
python scripts/replay_frozen_snapshot.py --replay-only --output ../m004_replay_output
```

This replays already frozen review classifications; it does not re-read source
papers, perform new human coding, regenerate manuscript figures, or validate
the reviewed models. docs/CURRENT_RUNTIME_CHECK.json records the two earlier
local replay checks. MANIFEST_SHA256.csv binds all archive files except itself.
