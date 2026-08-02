#!/usr/bin/env python3
"""Apply the signed WP9.8 author review to a versioned analysis core.

The locked 70-paper corpus and its 57-paper quantitative membership are never
modified. Only the 51 signed field decisions and nine signed method-family
mappings are applied to prospective WP9.8-R1 outputs.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_CORE = ROOT / "evidence" / "IJGGC_V2_R2_FULLY_REVIEWED_CORE.csv"
BASE_METHODS = ROOT / "evidence" / "WP9_4_METHOD_FAMILY_MAPPING.csv"
FIELD_OVERRIDES = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_FIELD_OVERRIDES.csv"
METHOD_OVERRIDES = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_METHOD_MAPPINGS.csv"
CONFIG_PATH = ROOT / "config" / "ijggc_v2_wp8_analysis_config.json"

OUT_CORE = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_ANALYSIS_CORE.csv"
OUT_METHODS = ROOT / "evidence" / "WP9_8_R1_METHOD_FAMILY_MAPPING.csv"
OUT_DIMENSIONS = ROOT / "evidence" / "WP9_8_R1_DECISION_EVIDENCE_PROFILES.csv"
OUT_REGIMES = ROOT / "evidence" / "WP9_8_R1_EVIDENCE_REGIME_PROFILES.csv"
OUT_OUTCOMES = ROOT / "evidence" / "WP9_8_R1_VALIDATION_OUTCOME_PROFILES.csv"
OUT_SENSITIVITY = ROOT / "evidence" / "WP9_8_R1_SENSITIVITY_ANALYSIS_RESULTS.csv"
OUT_BEFORE_AFTER = ROOT / "validation" / "WP9_8_R1_BEFORE_AFTER.csv"
OUT_REPORT = ROOT / "validation" / "WP9_8_R1_INTEGRATION_REPORT.md"
OUT_MANIFEST = ROOT / "validation" / "WP9_8_R1_ANALYSIS_MANIFEST.json"

VERSION = "WP9.8-R1-AUTHOR-VERIFIED-2026-08-01"
EXPECTED_BASE_CORE_SHA256 = "294623b5013989b6476b545dc0aeeaeb849054c235e58ae4c8f087793340317d"
EXPECTED_WORKBOOK_SHA256 = "3ece3b766ddcd28748301a1f3b894a6012dcf9d2a3a1aea810f645303c29e1fe"
EXPECTED_FIELD_COUNT = 51
EXPECTED_METHOD_COUNT = 9
EXPECTED_CORE_N = 70
EXPECTED_MAIN_N = 57


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    required = [BASE_CORE, BASE_METHODS, FIELD_OVERRIDES, METHOD_OVERRIDES, CONFIG_PATH]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing WP9.8-R1 input(s): " + "; ".join(missing))
    actual_base_hash = sha256(BASE_CORE)
    if actual_base_hash != EXPECTED_BASE_CORE_SHA256:
        raise ValueError(f"Locked WP8-R2 core hash changed: {actual_base_hash}")

    field_overrides = read_csv(FIELD_OVERRIDES)
    method_overrides = read_csv(METHOD_OVERRIDES)
    if len(field_overrides) != EXPECTED_FIELD_COUNT:
        raise ValueError(f"Expected {EXPECTED_FIELD_COUNT} field overrides, found {len(field_overrides)}")
    if len(method_overrides) != EXPECTED_METHOD_COUNT:
        raise ValueError(f"Expected {EXPECTED_METHOD_COUNT} method mappings, found {len(method_overrides)}")
    workbook_hashes = {row["source_workbook_sha256"].lower() for row in field_overrides + method_overrides}
    if workbook_hashes != {EXPECTED_WORKBOOK_SHA256}:
        raise ValueError(f"Unexpected workbook hashes: {sorted(workbook_hashes)}")

    wp4 = load_module(
        "wp4_for_wp9_8_r1",
        ROOT / "scripts" / "journal_neutral" / "build_wp4_quantitative_synthesis.py",
    )
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["analysis_version"] = VERSION
    config["analysis_status"] = "author_verified_wp9_8_r1_controlled_integration"

    original_rows = read_csv(BASE_CORE)
    core_rows = read_csv(BASE_CORE)
    if len(core_rows) != EXPECTED_CORE_N:
        raise ValueError(f"Expected {EXPECTED_CORE_N} core rows, found {len(core_rows)}")
    core_by_id = {row["paper_id"]: row for row in core_rows}
    if len(core_by_id) != len(core_rows):
        raise ValueError("Duplicate paper_id in locked core")

    before_after: list[dict[str, object]] = []
    changed_by_paper: Counter[str] = Counter()
    for override in field_overrides:
        paper_id = override["paper_id"]
        if paper_id not in core_by_id:
            raise ValueError(f"Field override references unknown paper_id {paper_id}")
        row = core_by_id[paper_id]
        category_field = override["category_field"]
        target_category_field = (
            "wp9_8_r1_physical_diagnostic_category"
            if category_field == "physical_diagnostic_fields"
            else category_field
        )
        score_field = override["score_field"]
        old_category = row.get(target_category_field, "")
        old_score = row.get(score_field, "")
        row[target_category_field] = override["final_category"]
        row[f"{target_category_field}_source"] = (
            f"{VERSION}; {override['review_item_id']}; {override['evidence_page_or_section']}"
        )
        row[score_field] = override["final_score"]
        row[f"{score_field}_state"] = override["score_state"]
        row[f"{score_field}_state_source"] = (
            f"{VERSION}; {override['review_item_id']}; signed author review by {override['reviewer_name']}"
        )
        row["wp9_8_r1_author_review_status"] = "signed_author_verified"
        row["wp9_8_r1_author_reviewer"] = override["reviewer_name"]
        row["wp9_8_r1_author_review_date"] = override["review_date"]
        row["wp9_8_r1_author_review_workbook_sha256"] = override["source_workbook_sha256"]
        changed_by_paper[paper_id] += 1
        before_after.append(
            {
                "review_item_id": override["review_item_id"],
                "paper_id": paper_id,
                "dimension": override["dimension"],
                "category_field": target_category_field,
                "prior_category": old_category,
                "final_category": override["final_category"],
                "score_field": score_field,
                "prior_score": old_score,
                "final_score": override["final_score"],
                "score_state": override["score_state"],
                "review_decision": override["review_decision"],
                "evidence_page_or_section": override["evidence_page_or_section"],
                "decision_rationale": override["decision_rationale"],
                "reviewer_name": override["reviewer_name"],
                "review_date": override["review_date"],
                "source_workbook_sha256": override["source_workbook_sha256"],
            }
        )

    for row in core_rows:
        row["wp9_8_r1_analysis_version"] = VERSION
        row["wp9_8_r1_changed_field_item_count"] = str(changed_by_paper[row["paper_id"]])
        if not row.get("wp9_8_r1_author_review_status"):
            row["wp9_8_r1_author_review_status"] = "no_targeted_wp9_8_override"

    main_rows = [row for row in core_rows if wp4.is_main_claim_eligible(row, config)]
    if len(main_rows) != EXPECTED_MAIN_N:
        raise ValueError(f"Main quantitative universe changed: {len(main_rows)} != {EXPECTED_MAIN_N}")

    dimension_rows, dimension_trace = wp4.build_dimension_profiles(main_rows, config)
    outcome_rows, outcome_trace = wp4.build_validation_profiles(main_rows, config)
    regime_rows = wp4.build_regime_profiles(main_rows, config)
    sensitivity_rows = wp4.build_sensitivity_results(core_rows, original_rows, config)

    method_rows = read_csv(BASE_METHODS)
    method_by_id = {row["paper_id"]: row for row in method_rows}
    if len(method_rows) != EXPECTED_MAIN_N or len(method_by_id) != EXPECTED_MAIN_N:
        raise ValueError("WP9.4 method mapping is not a unique 57-paper map")
    for override in method_overrides:
        paper_id = override["paper_id"]
        if paper_id not in method_by_id:
            raise ValueError(f"Method override references unknown paper_id {paper_id}")
        row = method_by_id[paper_id]
        row["primary_method_family_id"] = override["final_primary_family"]
        row["secondary_method_family_id"] = override["final_secondary_family"]
        row["mapping_status"] = "author_verified_wp9_8_r1"
        row["mapping_confidence"] = "author_verified"
        row["mapping_basis"] = override["decision_rationale"]
        row["ambiguity_note"] = "Resolved by signed WP9.8-R1 author review."
        row["wp9_8_r1_review_item_id"] = override["review_item_id"]
        row["wp9_8_r1_reviewer"] = override["reviewer_name"]
        row["wp9_8_r1_review_date"] = override["review_date"]
        row["wp9_8_r1_evidence_locator"] = override["evidence_page_or_section"]
        row["wp9_8_r1_source_workbook_sha256"] = override["source_workbook_sha256"]
    for row in method_rows:
        row["wp9_8_r1_analysis_version"] = VERSION

    write_csv(OUT_CORE, core_rows)
    write_csv(OUT_METHODS, method_rows)
    write_csv(OUT_DIMENSIONS, dimension_rows)
    write_csv(OUT_REGIMES, regime_rows)
    write_csv(OUT_OUTCOMES, outcome_rows)
    write_csv(OUT_SENSITIVITY, sensitivity_rows)
    write_csv(OUT_BEFORE_AFTER, before_after)

    all_dimensions = [row for row in dimension_rows if row["application_group"] == "ALL"]
    all_outcomes = [row for row in outcome_rows if row["application_group"] == "ALL"]
    headline_dimensions = {row["dimension"]: int(row["score_ge3_n"]) for row in all_dimensions}
    headline_outcomes = {row["outcome"]: int(row["positive_n"]) for row in all_outcomes}
    method_counts = Counter(row["primary_method_family_id"] for row in method_rows)

    manifest = {
        "analysis_version": VERSION,
        "base_core": str(BASE_CORE.relative_to(ROOT)).replace("\\", "/"),
        "base_core_sha256": actual_base_hash,
        "source_workbook_sha256": EXPECTED_WORKBOOK_SHA256,
        "core_N": len(core_rows),
        "main_N": len(main_rows),
        "field_override_rows": len(field_overrides),
        "method_mapping_rows": len(method_overrides),
        "field_override_paper_count": len(changed_by_paper),
        "headline_score_ge3_counts": headline_dimensions,
        "headline_validation_positive_counts": headline_outcomes,
        "primary_method_family_counts": dict(sorted(method_counts.items())),
        "outputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in [OUT_CORE, OUT_METHODS, OUT_DIMENSIONS, OUT_REGIMES, OUT_OUTCOMES, OUT_SENSITIVITY, OUT_BEFORE_AFTER]
        },
        "traceability_rows_generated_in_memory": len(dimension_trace) + len(outcome_trace),
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    OUT_REPORT.write_text(
        "\n".join(
            [
                "# WP9.8-R1 controlled integration report",
                "",
                f"- Analysis version: `{VERSION}`.",
                f"- Locked core retained: {len(core_rows)} records; main quantitative universe retained: N={len(main_rows)}.",
                f"- Signed field decisions applied: {len(field_overrides)} rows across {len(changed_by_paper)} papers.",
                f"- Signed method-family decisions applied: {len(method_overrides)} rows.",
                "- Corpus membership, bibliographic identity and claim eligibility were not changed.",
                "- Unknown, unclear and not reported states were not converted to zero.",
                "- Physical-consistency aggregate decisions were stored in a WP9.8-R1 aggregate field; component diagnostics were not inferred.",
                "",
                "## Headline score >=3 counts",
                "",
                *[f"- {key}: {value}" for key, value in headline_dimensions.items()],
                "",
                "## Headline validation outcome counts",
                "",
                *[f"- {key}: {value}" for key, value in headline_outcomes.items()],
                "",
                "## Method-family counts",
                "",
                *[f"- {key or 'not assigned'}: {value}" for key, value in sorted(method_counts.items())],
                "",
                "The outputs are prospective derived artifacts. They do not overwrite the locked WP8-R2 core or the WP9.4 mapping ledger.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
