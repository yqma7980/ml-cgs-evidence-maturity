from __future__ import annotations

import csv
import json
import math
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "supplementary" / "ijggc" / "v2"
DEST = ROOT / "supplementary" / "ijggc" / "v2_wp8_r2"
RAW_SEARCH = ROOT / "validation" / "search_update_raw"
REFERENCE_METADATA_OVERRIDES = ROOT / "config" / "ijggc_v2_reference_metadata_overrides.json"

LU2022_METADATA = {
    "title": "Bayesian Optimization for Field-Scale Geological Carbon Storage",
    "authors": "Xueying Lu; Kirk E. Jordan; Mary F. Wheeler; Edward O. Pyzer-Knapp; Matthew Benatan",
    "year": "2022",
    "venue": "Engineering",
    "doi_or_url": "https://doi.org/10.1016/j.eng.2022.06.011",
}


def load_reference_metadata_overrides() -> dict[str, dict[str, str]]:
    return json.loads(REFERENCE_METADATA_OVERRIDES.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sanitize_public_value(value: str) -> str:
    text = (value or "").strip()
    normalized = text.replace("\\", "/")
    root = str(ROOT).replace("\\", "/")
    if normalized.lower().startswith(root.lower() + "/"):
        return normalized[len(root) + 1 :]
    if "c:/users/" in normalized.lower():
        return "Local source path withheld; see repository-relative evidence records"
    return text


def public_source(value: str, doi_or_url: str) -> str:
    value = sanitize_public_value(value)
    normalized = value.replace("\\", "/").lower()
    doi_or_url = (doi_or_url or "").strip()
    if value.startswith(("https://", "http://")):
        return value
    # Public screening ledgers identify the accessible source, not the
    # author's local PDF inventory. Prefer DOI/URL whenever the recorded source
    # is a repository-relative or absolute local file path.
    is_local_file = (
        "literature/full_text" in normalized
        or normalized.endswith(".pdf")
        or normalized.startswith("local source path withheld")
    )
    if value and not is_local_file:
        return value
    if doi_or_url.startswith(("https://", "http://")):
        return doi_or_url
    if doi_or_url.startswith("10."):
        return f"https://doi.org/{doi_or_url}"
    return "Full text verified from an author-held or repository copy"


def build_screening_ledger() -> None:
    rows = read_csv(SOURCE / "TableS07_master_screening_ledger.csv")
    overrides = load_reference_metadata_overrides()
    fields = [
        "record_id", "title", "authors", "year", "venue", "doi_or_url",
        "record_class", "current_status", "full_text_verified",
        "full_text_source", "full_text_version", "main_quantitative_inclusion",
        "status_or_exclusion_reason", "evidence_page_or_section_note",
        "source_inventory", "application_group", "notes",
    ]
    output: list[dict[str, object]] = []
    for row in rows:
        item = {field: sanitize_public_value(row.get(field, "")) for field in fields}
        if row.get("record_id") == "Lu2022_BayesianOptimization":
            item.update(LU2022_METADATA)
        if row.get("record_id") in overrides:
            item.update({key: value for key, value in overrides[row["record_id"]].items() if key in fields})
        item["full_text_source"] = public_source(
            row.get("full_text_source_or_path", ""), item.get("doi_or_url", "")
        )
        if not item["current_status"]:
            if item["record_class"] == "excluded_decision_record":
                item["current_status"] = "excluded_from_primary_synthesis"
            elif str(item["main_quantitative_inclusion"]).lower() == "yes":
                item["current_status"] = "quantitative_main"
            else:
                item["current_status"] = "not_in_main_quantitative_synthesis"
        output.append(item)
    write_csv(DEST / "TableS07_master_screening_ledger.csv", output, fields)


def copy_clean_table(name: str) -> None:
    rows = read_csv(SOURCE / name)
    overrides = load_reference_metadata_overrides()
    fields = list(rows[0]) if rows else []
    cleaned = [
        {field: sanitize_public_value(row.get(field, "")) for field in fields}
        for row in rows
    ]
    if name == "TableS09a_publication_status_normalization.csv":
        for item in cleaned:
            if item.get("paper_id") == "Lu2022_BayesianOptimization":
                item.update(
                    {
                        "title": LU2022_METADATA["title"],
                        "venue": LU2022_METADATA["venue"],
                        "doi_or_url": "10.1016/j.eng.2022.06.011",
                        "normalization_basis": (
                            "Verified against the full-text first page; the legacy "
                            "Crossref match referred to an unrelated Engineering article."
                        ),
                        "crossref_type": "journal-article",
                        "normalized_publication_status": "peer_reviewed_journal",
                        "included_in_strict_journal_only_sensitivity": "yes",
                    }
                )
            paper_id = item.get("paper_id", "")
            if paper_id in overrides:
                metadata = overrides[paper_id]
                item.update(
                    {
                        "title": metadata["title"],
                        "venue": metadata["venue"],
                        "doi_or_url": metadata["doi_or_url"].removeprefix("https://doi.org/"),
                        "normalization_basis": metadata["verification_basis"],
                        "crossref_type": "journal-article",
                        "normalized_publication_status": "peer_reviewed_journal",
                        "included_in_strict_journal_only_sensitivity": "yes",
                    }
                )
    write_csv(DEST / name, cleaned, fields)


def build_search_log() -> None:
    rows = read_csv(SOURCE / "TableS10_update_search_log.csv")
    fields = list(rows[0]) if rows else []
    error_by_file: dict[str, dict[str, str]] = {}
    for path in RAW_SEARCH.rglob("search_*.json"):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        errors = payload.get("errors") or {}
        error_by_file[path.name] = {str(k): str(v) for k, v in errors.items()}

    output: list[dict[str, object]] = []
    for row in rows:
        item = {field: sanitize_public_value(row.get(field, "")) for field in fields}
        errors = error_by_file.get(row.get("search_file", ""), {})
        source = row.get("source", "")
        if source in errors:
            item["error"] = errors[source]
        output.append(item)
    write_csv(DEST / "TableS10_update_search_log.csv", output, fields)


def build_strict_sensitivity() -> None:
    rows = read_csv(ROOT / "evidence" / "IJGGC_V2_R2_SENSITIVITY_ANALYSIS_RESULTS.csv")
    selected = [row for row in rows if row.get("scenario") == "peer_reviewed_journal_only"]
    fields = [
        "analysis_universe", "metric", "N", "positive", "available",
        "missing_or_unavailable", "observed_fraction_of_total",
        "positive_paper_ids", "interpretation",
    ]
    output: list[dict[str, object]] = []
    for row in selected:
        output.append(
            {
                "analysis_universe": "Peer-reviewed journal-only sensitivity set",
                "metric": row.get("metric", ""),
                "N": row.get("scenario_total_N", ""),
                "positive": row.get("numerator", ""),
                "available": row.get("denominator", ""),
                "missing_or_unavailable": row.get("missing_or_unavailable_n", ""),
                "observed_fraction_of_total": row.get("observed_fraction_of_scenario_total", ""),
                "positive_paper_ids": row.get("positive_paper_ids", ""),
                "interpretation": (
                    "Descriptive sensitivity count only; the corpus is not a random sample and "
                    "no population-prevalence inference is intended."
                ),
            }
        )
    write_csv(DEST / "TableS09_journal_only_sensitivity.csv", output, fields)


def build_full_review_matrix() -> None:
    rows = read_csv(ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv")
    fields = [
        "paper_id", "field", "locked_value", "reviewer_value", "final_value",
        "decision_basis", "changed_from_locked", "reviewer_evidence", "author_evidence",
        "resolution_rationale", "reviewer", "adjudicator", "review_date",
        "adjudication_date", "review_batch", "source_workbook",
    ]
    cleaned = [
        {field: sanitize_public_value(row.get(field, "")) for field in fields}
        for row in rows
    ]
    write_csv(DEST / "TableS11_independent_review_final_matrix.csv", cleaned, fields)


def build_agreement_table() -> None:
    rows = read_csv(ROOT / "validation" / "IJGGC_V2_R2_INTERCODER_AGREEMENT.csv")
    fields = [
        "field", "sample_N", "comparable_n", "locked_baseline_unavailable_n",
        "exact_agreement_n", "exact_agreement_fraction", "cohen_kappa", "interpretation",
    ]
    write_csv(DEST / "TableS12_intercoder_agreement.csv", rows, fields)


def weighted_kappa(pairs: list[tuple[int, int]], quadratic: bool = False) -> float | None:
    if not pairs:
        return None
    categories = list(range(5))
    left = Counter(a for a, _ in pairs)
    right = Counter(b for _, b in pairs)
    total = len(pairs)

    def weight(a: int, b: int) -> float:
        distance = abs(a - b) / 4
        return 1 - (distance * distance if quadratic else distance)

    observed = sum(weight(a, b) for a, b in pairs) / total
    expected = sum(
        weight(a, b) * (left[a] / total) * (right[b] / total)
        for a in categories for b in categories
    )
    if math.isclose(1 - expected, 0.0):
        return None
    return (observed - expected) / (1 - expected)


def build_confusion_matrix() -> None:
    matrix = read_csv(ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv")
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in matrix:
        if row.get("decision_basis") == "author_verified_locked_baseline_unavailable":
            continue
        locked = row.get("locked_value", "").strip() or "blank"
        reviewer = row.get("reviewer_value", "").strip() or "blank"
        counts[(row.get("field", ""), locked, reviewer)] += 1
    fields = ["field", "locked_value", "independent_reviewer_value", "count"]
    rows = [
        {
            "field": field,
            "locked_value": locked,
            "independent_reviewer_value": reviewer,
            "count": count,
        }
        for (field, locked, reviewer), count in sorted(counts.items())
    ]
    write_csv(DEST / "TableS14_intercoder_confusion_matrix.csv", rows, fields)


def build_reliability_diagnostics() -> None:
    matrix = read_csv(ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv")
    agreement = {
        row["field"]: row
        for row in read_csv(ROOT / "validation" / "IJGGC_V2_R2_INTERCODER_AGREEMENT.csv")
    }
    score_fields = {
        "field_evidence_score", "physical_consistency_score", "uncertainty_score",
        "transferability_score", "decision_readiness_score",
    }
    fields = [
        "field", "comparable_n", "numeric_score_pairs_n", "exact_agreement_fraction",
        "unweighted_cohen_kappa", "linear_weighted_kappa", "quadratic_weighted_kappa",
        "locked_modal_value", "locked_modal_fraction", "reviewer_modal_value",
        "reviewer_modal_fraction", "marginal_imbalance_note", "interpretation",
    ]
    output: list[dict[str, object]] = []
    for field_name in sorted(agreement):
        rows = [
            row for row in matrix
            if row.get("field") == field_name
            and row.get("decision_basis") != "author_verified_locked_baseline_unavailable"
        ]
        locked = Counter((row.get("locked_value", "").strip() or "blank") for row in rows)
        reviewer = Counter((row.get("reviewer_value", "").strip() or "blank") for row in rows)
        locked_mode, locked_n = locked.most_common(1)[0]
        reviewer_mode, reviewer_n = reviewer.most_common(1)[0]
        numeric_pairs = [
            (int(row["locked_value"]), int(row["reviewer_value"]))
            for row in rows
            if row.get("locked_value", "").strip() in {"0", "1", "2", "3", "4"}
            and row.get("reviewer_value", "").strip() in {"0", "1", "2", "3", "4"}
        ]
        linear = weighted_kappa(numeric_pairs, quadratic=False) if field_name in score_fields else None
        quadratic = weighted_kappa(numeric_pairs, quadratic=True) if field_name in score_fields else None
        a = agreement[field_name]
        output.append(
            {
                "field": field_name,
                "comparable_n": len(rows),
                "numeric_score_pairs_n": len(numeric_pairs),
                "exact_agreement_fraction": a.get("exact_agreement_fraction", ""),
                "unweighted_cohen_kappa": a.get("cohen_kappa", ""),
                "linear_weighted_kappa": "" if linear is None else f"{linear:.6f}",
                "quadratic_weighted_kappa": "" if quadratic is None else f"{quadratic:.6f}",
                "locked_modal_value": locked_mode,
                "locked_modal_fraction": f"{locked_n / len(rows):.6f}",
                "reviewer_modal_value": reviewer_mode,
                "reviewer_modal_fraction": f"{reviewer_n / len(rows):.6f}",
                "marginal_imbalance_note": (
                    "Kappa is sensitive to the strongly imbalanced coder marginals; "
                    "interpret together with raw agreement and the confusion matrix."
                    if max(locked_n, reviewer_n) / len(rows) >= 0.70 else
                    "Coder marginals are less concentrated, but kappa still requires the confusion matrix."
                ),
                "interpretation": (
                    "Weighted kappa is reported only for numeric 0-4 score pairs; "
                    "missing, unclear, and not-reported values are excluded from weighted calculations."
                ),
            }
        )
    write_csv(DEST / "TableS15_intercoder_reliability_diagnostics.csv", output, fields)


def build_adjudication_dependence_sensitivity() -> None:
    matrix = read_csv(ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv")
    positive_values = {
        "field_validation_category": {
            "field_observation_comparison", "controlled_field_evaluation", "field_workflow_evaluation",
        },
        "controlled_release_validation_state": {"ml_evaluated_on_controlled_release"},
        "ood_test_category": {"legacy_explicit_ood_test", "cross_site_heldout"},
        "cross_site_test_state": {"explicit_heldout_cross_site_test"},
        "uncertainty_calibration_category": {
            "calibrated_or_posterior_checked", "legacy_uncertainty_calibration_or_posterior_check",
        },
        "surrogate_error_propagation_category": {"propagated_into_inference_or_decision"},
    }
    labels = {
        "field_validation_category": "direct_field_evaluation",
        "controlled_release_validation_state": "controlled_release_or_planned_experimental_injection_evaluation",
        "ood_test_category": "explicit_ood_testing",
        "cross_site_test_state": "explicit_cross_site_or_cross_setting_testing",
        "uncertainty_calibration_category": "uncertainty_calibration_or_posterior_checking",
        "surrogate_error_propagation_category": "surrogate_error_propagation",
    }
    score_fields = [
        "field_evidence_score", "physical_consistency_score", "uncertainty_score",
        "transferability_score", "decision_readiness_score",
    ]
    fields = [
        "reported_metric", "source_field", "positive_rule", "final_positive_n",
        "positive_exact_agreement_n", "positive_author_adjudicated_n",
        "positive_baseline_unavailable_verified_n", "interpretation",
    ]
    output: list[dict[str, object]] = []

    def append_metric(label: str, source_field: str, rule: str, rows: list[dict[str, str]]) -> None:
        selected = [row for row in rows if row.get("_positive") == "yes"]
        basis = Counter(row.get("decision_basis", "") for row in selected)
        output.append(
            {
                "reported_metric": label,
                "source_field": source_field,
                "positive_rule": rule,
                "final_positive_n": len(selected),
                "positive_exact_agreement_n": basis.get("independent_exact_agreement_retained", 0),
                "positive_author_adjudicated_n": basis.get("author_adjudicated_disagreement", 0),
                "positive_baseline_unavailable_verified_n": basis.get("author_verified_locked_baseline_unavailable", 0),
                "interpretation": (
                    "This is an adjudication-dependence audit, not an alternative prevalence estimate. "
                    "It shows which positive findings survive without relying on a disagreement resolution."
                ),
            }
        )

    for source_field, values in positive_values.items():
        rows = [dict(row) for row in matrix if row.get("field") == source_field]
        for row in rows:
            row["_positive"] = "yes" if row.get("final_value") in values else "no"
        append_metric(labels[source_field], source_field, "final categorical value in positive set", rows)

    for source_field in score_fields:
        rows = [dict(row) for row in matrix if row.get("field") == source_field]
        for row in rows:
            value = row.get("final_value", "").strip()
            row["_positive"] = "yes" if value in {"3", "4"} else "no"
        append_metric(source_field + "_ge_3", source_field, "final numeric score >= 3", rows)

    write_csv(DEST / "TableS16_adjudication_dependence_sensitivity.csv", output, fields)


def build_review_summary() -> None:
    matrix = read_csv(ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv")
    agreement = read_csv(ROOT / "validation" / "IJGGC_V2_R2_INTERCODER_AGREEMENT.csv")
    exact = sum(row.get("decision_basis") == "independent_exact_agreement_retained" for row in matrix)
    adjudicated = sum(row.get("decision_basis") == "author_adjudicated_disagreement" for row in matrix)
    unavailable = sum(
        row.get("decision_basis") == "author_verified_locked_baseline_unavailable"
        for row in matrix
    )
    comparable = sum(int(float(row.get("comparable_n", 0) or 0)) for row in agreement)
    exact_pre = sum(int(float(row.get("exact_agreement_n", 0) or 0)) for row in agreement)
    kappas = [float(row["cohen_kappa"]) for row in agreement if row.get("cohen_kappa", "").strip()]
    fields = ["item", "value", "interpretation"]
    rows = [
        {"item": "independently_reviewed_papers", "value": 57, "interpretation": "All papers in the main quantitative universe."},
        {"item": "coded_fields_per_paper", "value": 11, "interpretation": "Six categorical evidence fields and five 0-4 maturity dimensions."},
        {"item": "final_paper_field_items", "value": len(matrix), "interpretation": "Final human-reviewed paper-field matrix."},
        {"item": "pre_adjudication_comparable_items", "value": comparable, "interpretation": "Items with both a locked baseline and an independent reviewer value."},
        {"item": "pre_adjudication_exact_agreements", "value": exact_pre, "interpretation": "Exact agreement before adjudication."},
        {"item": "pre_adjudication_exact_agreement_fraction", "value": f"{exact_pre / comparable:.6f}", "interpretation": "Descriptive agreement before adjudication, not final consensus agreement."},
        {"item": "exact_agreements_retained_in_final_matrix", "value": exact, "interpretation": "Locked and independent values matched exactly."},
        {"item": "disagreements_author_adjudicated", "value": adjudicated, "interpretation": "Resolved against full-text evidence and the coding manual."},
        {"item": "baseline_unavailable_items_author_verified", "value": unavailable, "interpretation": "No pre-existing value was available for independent comparison; final value was verified from full text."},
        {"item": "field_level_kappa_range", "value": f"{min(kappas):.3f}-{max(kappas):.3f}", "interpretation": "Pre-adjudication field-level Cohen's kappa range."},
        {"item": "machine_proposed_resolutions_adopted_without_human_verification", "value": 0, "interpretation": "No machine-proposed resolution entered the reported synthesis without paper-level human verification."},
    ]
    write_csv(DEST / "TableS13_independent_review_summary.csv", rows, fields)


def copy_raw_search_logs() -> None:
    target = DEST / "search_update_raw"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(RAW_SEARCH, target)


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    build_screening_ledger()
    copy_clean_table("TableS08_decision_application_crosswalk.csv")
    copy_clean_table("TableS09a_publication_status_normalization.csv")
    build_strict_sensitivity()
    build_search_log()
    build_full_review_matrix()
    build_agreement_table()
    build_confusion_matrix()
    build_reliability_diagnostics()
    build_adjudication_dependence_sensitivity()
    build_review_summary()
    copy_raw_search_logs()
    print(f"WP8-R2 supplementary package complete: {DEST}")


if __name__ == "__main__":
    main()
