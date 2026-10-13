# Reproduction scope and non-execution record

This is the original preparation-scope record. Subsequent packaging-closure
runtime checks are recorded in CURRENT_COMPLETENESS_AND_RUNTIME_CHECK.md and
CURRENT_RUNTIME_CHECK.json. The original non-execution statements below concern
the earlier preparation, not the current verification status.

Preparation reads/copies/projects/hashes already frozen data; it does not import
or execute any derivation module, reclassify evidence, calculate scientific
indicators/scores, apply approvals, run simulation, or render manuscript content.
Coverage checks count stored rows/states and compare existing reported signatures.

scripts/replay_frozen_snapshot.py contains the own original replay() calculation
body and read/write/hash helpers. freeze(), deliver(), original private globals,
unused imports and default consolidation are not redistributed. The four exact
text replacements and integrity-only insertion are in TRANSFORMATIONS.json.
DERIVATION_RULES_FROZEN.json is byte-exact, including its original full-history
hash. PORTABLE_BINDINGS.json binds original and anonymous-curated history hashes;
only the runtime integrity reference is switched to the projected bytes.
Scientific category/score/membership/mapping/count rules are not changed.

The curated unit table retains every field required by replay(). Membership and
historical outputs will use the retained public columns, not private review
names, workbook paths, messages or approvals. Numerical outputs are the current
frozen outputs. Replay does not reproduce copyrighted source access, human
verification, new publication equivalence or public availability.

AST syntax checks and input-field inspection were performed; runtime replay was
NOT performed. This is an explicit testing gap, not a reproduction PASS claim.
After a separate authorization, an opt-in standard-library-only command is:

```text
python scripts/replay_frozen_snapshot.py --replay-only --output ../separate_replay_output
```

The output must be outside archive content. The packaged input/rule hashes and
all protected scientific cells must remain unchanged. Results must be compared
against the archived projected/byte-exact outputs before claiming reproduction.

Current-codebook excerpts are documentation only. Original historical codebook
example/recheck queue paths are deliberately not supplied as a current pending
queue. Old search/approval/production scripts, historical staging inputs and
manuscript/figure rendering are excluded. Historical scenario comparison outputs
are preserved as prior outputs; they are not recomputed by this limited replay.
