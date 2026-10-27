# Frozen scientific replay

Run from the release root (the parent of this directory), with Python 3.11+:

    python portable_replay/scripts/replay_frozen_snapshot.py --replay-only --output ../m004_replay_output
    python verify_replay_outputs.py --output ../m004_replay_output

Use a new output directory, not an archive input directory. All 58 generated scientific CSVs are compared. No network or extra packages are required. The unchanged script reconstructs frozen derived results; it does not perform new source classification or independent human review. The root README and release_notes/REPLAY_VERIFICATION.json give the current release status and observed local checks. Historical preparation wording within inherited source comments does not describe the current publication state.
