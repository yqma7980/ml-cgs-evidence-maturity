"""Verify existing frozen-table replay; never classify or write scientific inputs."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def verify(output, reference):
    checks = []
    missing = []
    for path in sorted(output.glob("*.csv")):
        target = reference / path.name
        if not target.is_file():
            missing.append(path.name)
            continue
        fields, values = rows(path)
        ref_fields, ref_values = rows(target)
        if set(fields) != set(ref_fields):
            raise AssertionError(f"Column mismatch: {path.name}")
        observed = Counter(tuple(value[field] for field in fields) for value in values)
        expected = Counter(tuple(value[field] for field in fields) for value in ref_values)
        if observed != expected:
            raise AssertionError(f"Row/value mismatch: {path.name}")
        checks.append({"filename": path.name, "rows": len(values), "match": True})
    if missing:
        raise AssertionError(f"Unmatched output files: {missing}")
    if len(checks) != 58:
        raise AssertionError(f"Expected all 58 replay CSVs, got {len(checks)}")
    return {"status": "PASS", "scientific_CSVs_checked": len(checks), "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    reference = args.reference or root / "portable_replay/data"
    print(json.dumps(verify(args.output.resolve(), reference.resolve()), indent=2))
