#!/usr/bin/env python3
"""Validate the signed WP9.8-R1 controlled integration."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_CORE = ROOT / "evidence" / "IJGGC_V2_R2_FULLY_REVIEWED_CORE.csv"
CORE = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_ANALYSIS_CORE.csv"
BASE_METHODS = ROOT / "evidence" / "WP9_4_METHOD_FAMILY_MAPPING.csv"
METHODS = ROOT / "evidence" / "WP9_8_R1_METHOD_FAMILY_MAPPING.csv"
FIELDS = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_FIELD_OVERRIDES.csv"
METHOD_OVERRIDES = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_METHOD_MAPPINGS.csv"
DIMENSIONS = ROOT / "evidence" / "WP9_8_R1_DECISION_EVIDENCE_PROFILES.csv"
OUTCOMES = ROOT / "evidence" / "WP9_8_R1_VALIDATION_OUTCOME_PROFILES.csv"
MANIFEST = ROOT / "validation" / "WP9_8_R1_ANALYSIS_MANIFEST.json"
REPORT = ROOT / "validation" / "WP9_8_R1_VALIDATION_REPORT.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    required = [BASE_CORE, CORE, BASE_METHODS, METHODS, FIELDS, METHOD_OVERRIDES, DIMENSIONS, OUTCOMES, MANIFEST]
    for path in required:
        checks.append((f"exists:{path.name}", path.exists(), str(path)))
    if not all(ok for _, ok, _ in checks):
        return finish(checks)

    base = read_csv(BASE_CORE)
    core = read_csv(CORE)
    base_methods = read_csv(BASE_METHODS)
    methods = read_csv(METHODS)
    fields = read_csv(FIELDS)
    method_overrides = read_csv(METHOD_OVERRIDES)
    dimensions = read_csv(DIMENSIONS)
    outcomes = read_csv(OUTCOMES)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    checks.extend(
        [
            ("locked_core_rows", len(base) == 70, f"found {len(base)}"),
            ("derived_core_rows", len(core) == 70, f"found {len(core)}"),
            ("paper_ids_unchanged", {r['paper_id'] for r in base} == {r['paper_id'] for r in core}, "70-paper identity set"),
            ("field_override_count", len(fields) == 51, f"found {len(fields)}"),
            ("method_override_count", len(method_overrides) == 9, f"found {len(method_overrides)}"),
            ("method_map_rows", len(methods) == 57, f"found {len(methods)}"),
            ("method_ids_unchanged", {r['paper_id'] for r in base_methods} == {r['paper_id'] for r in methods}, "57-paper method set"),
            ("manifest_main_N", manifest.get("main_N") == 57, str(manifest.get("main_N"))),
            ("manifest_core_N", manifest.get("core_N") == 70, str(manifest.get("core_N"))),
        ]
    )

    core_by_id = {row["paper_id"]: row for row in core}
    for item in fields:
        row = core_by_id[item["paper_id"]]
        category_field = (
            "wp9_8_r1_physical_diagnostic_category"
            if item["category_field"] == "physical_diagnostic_fields"
            else item["category_field"]
        )
        checks.append((f"field:{item['review_item_id']}:category", row.get(category_field) == item["final_category"], row.get(category_field, "")))
        checks.append((f"field:{item['review_item_id']}:score", row.get(item["score_field"]) == item["final_score"], row.get(item["score_field"], "")))
        checks.append((f"field:{item['review_item_id']}:state", row.get(f"{item['score_field']}_state") == item["score_state"], row.get(f"{item['score_field']}_state", "")))

    method_by_id = {row["paper_id"]: row for row in methods}
    for item in method_overrides:
        row = method_by_id[item["paper_id"]]
        checks.append((f"method:{item['review_item_id']}:primary", row.get("primary_method_family_id") == item["final_primary_family"], row.get("primary_method_family_id", "")))
        checks.append((f"method:{item['review_item_id']}:secondary", row.get("secondary_method_family_id", "") == item["final_secondary_family"], row.get("secondary_method_family_id", "")))

    score_fields = ["field_evidence_score", "physical_consistency_score", "uncertainty_score", "transferability_score", "decision_readiness_score"]
    prohibited = {"unknown", "unclear", "not_reported", "not reported", ""}
    bad_zero = []
    for item in fields:
        if item["final_score"] == "0" and item["score_state"].strip().lower() in prohibited:
            bad_zero.append(item["review_item_id"])
    checks.append(("unknown_not_zero", not bad_zero, ";".join(bad_zero) or "no prohibited zero conversion"))

    all_dimensions = [row for row in dimensions if row["application_group"] == "ALL"]
    all_outcomes = [row for row in outcomes if row["application_group"] == "ALL"]
    checks.append(("five_headline_dimensions", {r['dimension'] for r in all_dimensions} == set(score_fields), str(len(all_dimensions))))
    checks.append(("headline_outcomes_present", len(all_outcomes) >= 6, str(len(all_outcomes))))

    for relative, expected_hash in manifest.get("outputs", {}).items():
        path = ROOT / relative
        checks.append((f"manifest_hash:{path.name}", path.exists() and sha256(path) == expected_hash, expected_hash))

    return finish(checks)


def finish(checks: list[tuple[str, bool, str]]) -> int:
    passed = sum(ok for _, ok, _ in checks)
    failed = [(name, detail) for name, ok, detail in checks if not ok]
    lines = [
        "# WP9.8-R1 validation report",
        "",
        f"- Result: {'PASS' if not failed else 'FAIL'}",
        f"- Checks passed: {passed}/{len(checks)}",
        f"- Checks failed: {len(failed)}",
        "",
        "## Checks",
        "",
        *[f"- {'PASS' if ok else 'FAIL'}: `{name}` ({detail})" for name, ok, detail in checks],
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"WP9.8-R1 {'PASS' if not failed else 'FAIL'}: {passed}/{len(checks)} checks")
    for name, detail in failed:
        print(f"FAIL {name}: {detail}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
