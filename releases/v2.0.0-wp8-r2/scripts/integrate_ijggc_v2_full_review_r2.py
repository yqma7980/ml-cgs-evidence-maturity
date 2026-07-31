#!/usr/bin/env python3
"""Integrate the two completed IJGGC V2 review batches without mutating locked inputs."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE_CORE = ROOT / "evidence" / "IJGGC_V2_HUMAN_REVIEW_SYNCHRONIZED_CORE.csv"
PRIOR_MATRIX = ROOT / "evidence" / "IJGGC_V2_HUMAN_REVIEW_FINAL_MATRIX.csv"
REMAINING_COMPARISON = ROOT / "evidence" / "IJGGC_V2_REMAINING31_PRE_ADJUDICATION_COMPARISON.csv"
WORKBOOK = (
    ROOT / "outputs" / "ijggc_v2_remaining31_adjudication_2026-07-30"
    / "IJGGC_V2_REMAINING31_ADJUDICATION_WORKBOOK.xlsx"
)
ADJUDICATION_JSON = ROOT / "validation" / "wp8_r2_workbook_extract" / "remaining31_adjudication_rows.json"
CONFIG = ROOT / "config" / "ijggc_v2_wp8_analysis_config.json"
PUBLICATION_STATUS_NORMALIZATION = (
    ROOT / "supplementary" / "ijggc" / "v2" / "TableS09a_publication_status_normalization.csv"
)
REFERENCE_METADATA_OVERRIDES = ROOT / "config" / "ijggc_v2_reference_metadata_overrides.json"

VERSION = "IJGGC-V2-WP8-R2-FULL-57-PAPER-REVIEW-2026-07-30"
EXPECTED_BASE_CORE_SHA256 = "d351f4cfd97174a365fa76ab9d1916356292c5dd54a49e875146d1bc3f05c9f2"
EXPECTED_WORKBOOK_SHA256 = "746e47ecffb74aa34fb36158201678045273560515fddfca588206683c7d1592"

SYNC_CORE = ROOT / "evidence" / "IJGGC_V2_R2_FULLY_REVIEWED_CORE.csv"
FULL_MATRIX = ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv"
FINAL_DECISIONS = ROOT / "evidence" / "IJGGC_V2_R2_ADJUDICATED_DECISIONS.csv"
DIMENSIONS = ROOT / "evidence" / "IJGGC_V2_R2_DECISION_EVIDENCE_PROFILES.csv"
REGIMES = ROOT / "evidence" / "IJGGC_V2_R2_EVIDENCE_REGIME_PROFILES.csv"
OUTCOMES = ROOT / "evidence" / "IJGGC_V2_R2_VALIDATION_OUTCOME_PROFILES.csv"
SENSITIVITY = ROOT / "evidence" / "IJGGC_V2_R2_SENSITIVITY_ANALYSIS_RESULTS.csv"
BEFORE_AFTER = ROOT / "validation" / "IJGGC_V2_R2_BEFORE_AFTER.csv"
AGREEMENT = ROOT / "validation" / "IJGGC_V2_R2_INTERCODER_AGREEMENT.csv"
REPORT = ROOT / "validation" / "IJGGC_V2_WP8_R2_INTEGRATION_REPORT.md"
MANIFEST = ROOT / "validation" / "IJGGC_V2_WP8_R2_ANALYSIS_MANIFEST.json"

FIELDS = [
    "field_validation_category",
    "controlled_release_validation_state",
    "ood_test_category",
    "cross_site_test_state",
    "uncertainty_calibration_category",
    "surrogate_error_propagation_category",
    "field_evidence_score",
    "physical_consistency_score",
    "uncertainty_score",
    "transferability_score",
    "decision_readiness_score",
]
SCORE_FIELDS = set(FIELDS[6:])
REVIEWER = "Xiaoyang Zhang (XZ)"
ADJUDICATOR = "Yangqi Ma (YM)"
REVIEW_DATE = "2026-07-30"
ADJUDICATION_DATE = "2026-07-30"

# Bibliographic corrections verified directly against the full-text first page.
# These alter citation metadata only; the locked evidence coding and corpus
# membership remain unchanged.
BIBLIOGRAPHIC_OVERRIDES = {
    "Zhang2021_LearningInversionFreeForecast": {
        "title": "Accurate and Rapid Forecasts for Geologic Carbon Storage via Learning-Based Inversion-Free Prediction",
        "authors": "Dan Lu; Scott L. Painter; Nicholas A. Azzolina; Matthew Burton-Kelly; Tao Jiang; Cody Williamson",
        "year": "2022",
        "venue": "Frontiers in Energy Research",
        "doi_or_url": "https://doi.org/10.3389/fenrg.2021.752185",
        "article_type": "journal_article",
        "peer_review_status": "peer_reviewed_journal",
    },
    "Lu2022_BayesianOptimization": {
        "title": "Bayesian Optimization for Field-Scale Geological Carbon Storage",
        "authors": "Xueying Lu; Kirk E. Jordan; Mary F. Wheeler; Edward O. Pyzer-Knapp; Matthew Benatan",
        "year": "2022",
        "venue": "Engineering",
        "doi_or_url": "https://doi.org/10.1016/j.eng.2022.06.011",
        "article_type": "journal_article",
        "peer_review_status": "peer_reviewed_journal",
    },
    "ESR_RefNone_173": {
        "title": "Toward Estimating CO2 Solubility in Pure Water and Brine Using Cascade Forward Neural Network and Generalized Regression Neural Network: Application to CO2 Dissolution Trapping in Saline Aquifers",
        "authors": "Xinyuan Zou; Yingting Zhu; Jing Lv; Yuchi Zhou; Bin Ding; Weidong Liu; Kai Xiao; Qun Zhang",
        "year": "2024",
        "venue": "ACS Omega",
        "doi_or_url": "https://doi.org/10.1021/acsomega.3c07962",
        "article_type": "journal_article",
        "peer_review_status": "peer_reviewed_journal",
    },
}


def load_bibliographic_overrides() -> dict[str, dict[str, str]]:
    overrides = {key: dict(value) for key, value in BIBLIOGRAPHIC_OVERRIDES.items()}
    if REFERENCE_METADATA_OVERRIDES.exists():
        payload = json.loads(REFERENCE_METADATA_OVERRIDES.read_text(encoding="utf-8"))
        for paper_id, metadata in payload.items():
            overrides.setdefault(paper_id, {}).update(metadata)
    return overrides


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
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
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    observed = sum(a == b for a, b in pairs) / len(pairs)
    left = Counter(a for a, _ in pairs)
    right = Counter(b for _, b in pairs)
    categories = set(left) | set(right)
    expected = sum((left[c] / len(pairs)) * (right[c] / len(pairs)) for c in categories)
    if math.isclose(1.0 - expected, 0.0):
        return None
    return (observed - expected) / (1.0 - expected)


def excel_date(value: Any) -> str:
    raw = text(value)
    if not raw:
        return ADJUDICATION_DATE
    try:
        serial = float(raw)
    except ValueError:
        return raw.split()[0]
    return (datetime(1899, 12, 30) + timedelta(days=serial)).date().isoformat()


def main() -> None:
    required = [
        BASE_CORE, PRIOR_MATRIX, REMAINING_COMPARISON, WORKBOOK,
        ADJUDICATION_JSON, CONFIG, REFERENCE_METADATA_OVERRIDES,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing WP8-R2 input(s): " + "; ".join(missing))
    if sha256(BASE_CORE) != EXPECTED_BASE_CORE_SHA256:
        raise ValueError("The locked synchronized 70-paper core hash changed")
    if sha256(WORKBOOK) != EXPECTED_WORKBOOK_SHA256:
        raise ValueError("The completed remaining31 adjudication workbook hash changed")

    legacy = load_module(
        "ijggc_prior_integrator",
        ROOT / "scripts" / "journal_neutral" / "integrate_ijggc_v2_independent_review.py",
    )
    wp4 = load_module(
        "wp4_builder_r2",
        ROOT / "scripts" / "journal_neutral" / "build_wp4_quantitative_synthesis.py",
    )
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config["analysis_version"] = VERSION
    config["analysis_status"] = "full_57_paper_independent_review_with_author_adjudication"

    base_rows = read_csv(BASE_CORE)
    bibliographic_overrides = load_bibliographic_overrides()
    prior_matrix = read_csv(PRIOR_MATRIX)
    comparison = read_csv(REMAINING_COMPARISON)
    adjudications = json.loads(ADJUDICATION_JSON.read_text(encoding="utf-8"))
    if len(base_rows) != 70 or len(prior_matrix) != 286 or len(comparison) != 341 or len(adjudications) != 288:
        raise ValueError(
            "Expected base/prior/comparison/adjudication sizes 70/286/341/288; "
            f"found {len(base_rows)}/{len(prior_matrix)}/{len(comparison)}/{len(adjudications)}"
        )

    prior_ids = {row["paper_id"] for row in prior_matrix}
    remaining_ids = {row["paper_id"] for row in comparison}
    if len(prior_ids) != 26 or len(remaining_ids) != 31 or prior_ids & remaining_ids:
        raise ValueError("The 26-paper and remaining31 review batches are not disjoint and complete")
    for paper_id in remaining_ids:
        rows = [row for row in comparison if row["paper_id"] == paper_id]
        if len(rows) != 11 or {row["field"] for row in rows} != set(FIELDS):
            raise ValueError(f"Remaining31 paper does not have all 11 fields: {paper_id}")

    exact_rows = [row for row in comparison if text(row.get("exact_match")).lower() == "yes"]
    disagreement_rows = [row for row in comparison if text(row.get("exact_match")).lower() == "no"]
    if len(exact_rows) != 53 or len(disagreement_rows) != 288:
        raise ValueError("Remaining31 comparison must contain exactly 53 agreements and 288 disagreements")

    adjudication_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in adjudications:
        key = (text(row.get("paper_id")), text(row.get("field")))
        if key in adjudication_lookup:
            raise ValueError(f"Duplicate remaining31 adjudication: {key}")
        if text(row.get("resolution_status")).lower() != "complete":
            raise ValueError(f"Incomplete remaining31 adjudication: {key}")
        if text(row.get("adjudicator_name")) != "Yangqi Ma" or text(row.get("adjudicator_initials")) != "YM":
            raise ValueError(f"Missing named adjudicator sign-off: {key}")
        if not all(text(row.get(field)) for field in ("final_value", "adjudication_evidence", "adjudication_rationale")):
            raise ValueError(f"Missing final value/evidence/rationale: {key}")
        adjudication_lookup[key] = row
    expected_disagreement_keys = {(row["paper_id"], row["field"]) for row in disagreement_rows}
    if set(adjudication_lookup) != expected_disagreement_keys:
        raise ValueError("Adjudication keys do not match the 288 disagreement keys")

    remaining_matrix: list[dict[str, Any]] = []
    for row in comparison:
        paper_id, field = row["paper_id"], row["field"]
        locked = legacy.canonical(field, row.get("author_locked_value"))
        reviewer = legacy.canonical(field, row.get("reviewer_value"))
        key = (paper_id, field)
        if text(row.get("exact_match")).lower() == "yes":
            if locked != reviewer:
                raise ValueError(f"False exact-agreement flag: {key}")
            final = locked
            basis = "independent_exact_agreement_retained"
            author_evidence = ""
            rationale = "Reviewer and locked coding agreed exactly; the locked value was retained."
            adjudication_date = ""
        else:
            decision = adjudication_lookup[key]
            final = legacy.canonical(field, decision.get("final_value"))
            basis = "author_adjudicated_disagreement"
            author_evidence = text(decision.get("adjudication_evidence"))
            rationale = text(decision.get("adjudication_rationale"))
            adjudication_date = excel_date(decision.get("adjudication_date"))
        remaining_matrix.append(
            {
                "paper_id": paper_id,
                "field": field,
                "reviewer_value": reviewer,
                "locked_value": locked,
                "final_value": final,
                "decision_basis": basis,
                "changed_from_locked": "yes" if final != locked else "no",
                "reviewer_evidence": text(row.get("reviewer_evidence")),
                "author_evidence": author_evidence,
                "resolution_rationale": rationale,
                "reviewer": REVIEWER,
                "adjudicator": ADJUDICATOR if basis == "author_adjudicated_disagreement" else "",
                "review_date": REVIEW_DATE,
                "adjudication_date": adjudication_date,
                "source_workbook": str(WORKBOOK.relative_to(ROOT)),
                "review_batch": "remaining31",
            }
        )

    for row in prior_matrix:
        row["review_batch"] = "prior26"
    full_matrix = prior_matrix + remaining_matrix
    if len(full_matrix) != 627 or len({(row["paper_id"], row["field"]) for row in full_matrix}) != 627:
        raise ValueError("The combined full-review matrix is not 57 x 11 unique items")

    matrix_lookup = {(row["paper_id"], row["field"]): row for row in full_matrix}
    synchronized: list[dict[str, Any]] = []
    for source in base_rows:
        row: dict[str, Any] = dict(source)
        paper_id = row["paper_id"]
        if paper_id in remaining_ids:
            changed_fields: list[str] = []
            for field in FIELDS:
                item = matrix_lookup[(paper_id, field)]
                final = item["final_value"]
                if field in SCORE_FIELDS:
                    if final in {"unknown", "unclear", "not_reported"}:
                        row[field] = ""
                        row[f"{field}_state"] = final
                    else:
                        row[field] = final
                        row[f"{field}_state"] = "scored"
                    row[f"{field}_state_source"] = "ijggc_v2_wp8_r2_full_review"
                else:
                    row[field] = final
                    row[f"{field}_source"] = "ijggc_v2_wp8_r2_full_review"
                    legacy_field = {
                        "field_validation_category": "field_validated",
                        "controlled_release_validation_state": "controlled_release_validated",
                        "ood_test_category": "ood_tested",
                        "cross_site_test_state": "cross_site_tested",
                        "uncertainty_calibration_category": "uncertainty_calibrated",
                        "surrogate_error_propagation_category": "surrogate_error_propagated",
                    }[field]
                    row[legacy_field] = legacy.legacy_value(field, final)
                if item["changed_from_locked"] == "yes":
                    changed_fields.append(field)
            row["ijggc_v2_independent_review_status"] = "remaining31_independent_review_completed"
            row["ijggc_v2_independent_reviewer"] = REVIEWER
            row["ijggc_v2_author_adjudicator"] = ADJUDICATOR
            row["ijggc_v2_review_date"] = REVIEW_DATE
            row["ijggc_v2_adjudication_date"] = ADJUDICATION_DATE
            row["ijggc_v2_reviewed_fields"] = ";".join(FIELDS)
            row["ijggc_v2_changed_field_count"] = str(len(changed_fields))
            row["ijggc_v2_changed_fields"] = ";".join(changed_fields)
            row["ijggc_v2_review_workbook"] = str(WORKBOOK.relative_to(ROOT))
        if paper_id in prior_ids or paper_id in remaining_ids:
            row["ijggc_v2_full_review_status"] = "full_57_paper_independent_review_completed"
            row["ijggc_v2_review_batch"] = "prior26" if paper_id in prior_ids else "remaining31"
        else:
            row["ijggc_v2_full_review_status"] = "outside_main_quantitative_universe"
            row["ijggc_v2_review_batch"] = "not_applicable"
        row["ijggc_v2_analysis_version"] = VERSION
        if paper_id in bibliographic_overrides:
            row.update(bibliographic_overrides[paper_id])
            row["bibliographic_verification_note"] = (
                "Corrected from verified DOI, publisher, and full-text metadata during WP8-R2 final validation."
            )
        synchronized.append(row)

    main_rows = [row for row in synchronized if wp4.is_main_claim_eligible(row, config)]
    if len(main_rows) != 57 or {row["paper_id"] for row in main_rows} != prior_ids | remaining_ids:
        raise ValueError("The rebuilt N=57 main universe does not match the two human-review batches")

    dimension_rows, dimension_trace = wp4.build_dimension_profiles(main_rows, config)
    outcome_rows, outcome_trace = wp4.build_validation_profiles(main_rows, config)
    regime_rows = wp4.build_regime_profiles(main_rows, config)
    sensitivity_rows = wp4.build_sensitivity_results(synchronized, base_rows, config)
    normalized = read_csv(PUBLICATION_STATUS_NORMALIZATION)
    strict_ids = {
        row["paper_id"] for row in normalized
        if text(row.get("included_in_strict_journal_only_sensitivity")).lower() == "yes"
    }
    strict_rows = [row for row in main_rows if row["paper_id"] in strict_ids]
    if len(strict_ids) != 49 or len(strict_rows) != 49:
        raise ValueError("The audited strict journal-only sensitivity universe must remain N=49")
    sensitivity_rows = [
        row for row in sensitivity_rows
        if not (row["sensitivity_family"] == "peer_review_status" and row["scenario"] == "peer_reviewed_journal_only")
    ]
    recalculated: list[dict[str, object]] = []
    wp4.add_standard_metrics(recalculated, "peer_review_status", "peer_reviewed_journal_only", strict_rows, config)
    sensitivity_rows.extend(recalculated)
    for row in dimension_rows + outcome_rows + dimension_trace + outcome_trace:
        row["human_gate_status"] = "full_57_paper_independent_review_completed_and_author_adjudicated"

    agreement_rows: list[dict[str, Any]] = []
    for field in FIELDS:
        items = [row for row in full_matrix if row["field"] == field]
        pairs = [
            (legacy.canonical(field, row["reviewer_value"]), legacy.canonical(field, row["locked_value"]))
            for row in items if text(row.get("locked_value"))
        ]
        exact = sum(left == right for left, right in pairs)
        kappa = cohen_kappa(pairs)
        agreement_rows.append(
            {
                "field": field,
                "sample_N": 57,
                "comparable_n": len(pairs),
                "locked_baseline_unavailable_n": 57 - len(pairs),
                "exact_agreement_n": exact,
                "exact_agreement_fraction": f"{exact / len(pairs):.6f}" if pairs else "",
                "cohen_kappa": f"{kappa:.6f}" if kappa is not None else "",
                "interpretation": "pre_adjudication_independent_comparison_across_two_review_batches",
            }
        )

    before_after = [
        {
            "paper_id": row["paper_id"],
            "field": row["field"],
            "locked_before": row.get("locked_value", ""),
            "human_review_final": row["final_value"],
            "changed": row["changed_from_locked"],
            "decision_basis": row["decision_basis"],
            "review_batch": row["review_batch"],
            "resolution_rationale": row.get("resolution_rationale", ""),
        }
        for row in full_matrix
    ]

    write_csv(SYNC_CORE, synchronized)
    write_csv(FULL_MATRIX, full_matrix)
    write_csv(FINAL_DECISIONS, [row for row in full_matrix if row["decision_basis"] != "independent_exact_agreement_retained"])
    write_csv(DIMENSIONS, dimension_rows)
    write_csv(REGIMES, regime_rows)
    write_csv(OUTCOMES, outcome_rows)
    write_csv(SENSITIVITY, sensitivity_rows)
    write_csv(BEFORE_AFTER, before_after)
    write_csv(AGREEMENT, agreement_rows)

    basis_counts = Counter(row["decision_basis"] for row in full_matrix)
    batch_counts = Counter(row["review_batch"] for row in full_matrix)
    changed_counts = Counter(row["review_batch"] for row in full_matrix if row["changed_from_locked"] == "yes")
    # The profile files contain an ALL row followed by application-group rows.
    # Manuscript-wide counts must be read only from the ALL rows; otherwise a
    # later small group can silently overwrite the corpus total in the dict.
    outcome_counts = {
        row["outcome"]: int(row["positive_n"])
        for row in outcome_rows
        if row["application_group"] == "ALL"
    }
    score_counts = {
        row["dimension"]: int(row["score_ge3_n"])
        for row in dimension_rows
        if row["application_group"] == "ALL"
    }
    comparable = sum(int(row["comparable_n"]) for row in agreement_rows)
    exact = sum(int(row["exact_agreement_n"]) for row in agreement_rows)
    kappas = [float(row["cohen_kappa"]) for row in agreement_rows if row["cohen_kappa"]]

    manifest = {
        "analysis_version": VERSION,
        "generated": date.today().isoformat(),
        "base_core": str(BASE_CORE.relative_to(ROOT)),
        "base_core_sha256": sha256(BASE_CORE),
        "remaining31_workbook": str(WORKBOOK.relative_to(ROOT)),
        "remaining31_workbook_sha256": sha256(WORKBOOK),
        "locked_core_record_count": len(base_rows),
        "main_quantitative_record_count": len(main_rows),
        "reviewed_paper_count": len(prior_ids | remaining_ids),
        "full_matrix_item_count": len(full_matrix),
        "review_batch_item_counts": dict(batch_counts),
        "decision_basis_counts": dict(basis_counts),
        "changed_item_counts": dict(changed_counts),
        "pre_adjudication_comparable_items": comparable,
        "pre_adjudication_exact_items": exact,
        "pre_adjudication_exact_fraction": exact / comparable,
        "field_level_kappa_range": [min(kappas), max(kappas)],
        "main_validation_counts": outcome_counts,
        "score_ge_3_counts": score_counts,
        "strict_journal_only_record_count": len(strict_rows),
        "outputs": [
            str(path.relative_to(ROOT)) for path in
            (SYNC_CORE, FULL_MATRIX, FINAL_DECISIONS, DIMENSIONS, REGIMES, OUTCOMES, SENSITIVITY, BEFORE_AFTER, AGREEMENT)
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# IJGGC V2 WP8-R2 controlled-integration report",
                "",
                "- Status: **PASS**",
                f"- Locked 70-paper core preserved: `{BASE_CORE.relative_to(ROOT)}`",
                f"- Main quantitative universe: **N={len(main_rows)}**",
                "- Independent review batches: 26 papers + 31 papers",
                f"- Complete final matrix: **{len(full_matrix)} paper-field items**",
                f"- Exact agreements retained: {basis_counts['independent_exact_agreement_retained']}",
                f"- Author-adjudicated disagreements: {basis_counts['author_adjudicated_disagreement']}",
                f"- Baseline-unavailable items verified in the prior26 batch: {basis_counts['author_verified_locked_baseline_unavailable']}",
                f"- Pre-adjudication exact agreement: {exact}/{comparable} ({exact / comparable:.1%})",
                f"- Field-level Cohen kappa range: {min(kappas):.3f} to {max(kappas):.3f}",
                "- Machine-proposed WP3 resolutions adopted without human verification: 0",
                "",
                "## Rebuilt main-universe counts",
                "",
                *(f"- `{key}`: {value}/57" for key, value in outcome_counts.items()),
                *(f"- `{key}` score >= 3: {value}/57" for key, value in score_counts.items()),
                "",
                "## Interpretation boundary",
                "",
                "Agreement statistics describe the independent pre-adjudication comparisons only. "
                "The final matrix is an author-adjudicated evidence product and is not reported as post-adjudication reliability. "
                "Unknown, unclear, and not-reported values remain distinct from score zero.",
            ]
        ) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
