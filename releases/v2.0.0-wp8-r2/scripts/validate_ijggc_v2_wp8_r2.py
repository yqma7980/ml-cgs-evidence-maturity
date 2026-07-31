#!/usr/bin/env python3
"""Final deterministic gate for the IJGGC WP8-R2 controlled rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "validation" / "IJGGC_V2_WP8_R2_VALIDATION_REPORT.md"
MANIFEST = ROOT / "validation" / "IJGGC_V2_WP8_R2_ANALYSIS_MANIFEST.json"
CORE = ROOT / "evidence" / "IJGGC_V2_R2_FULLY_REVIEWED_CORE.csv"
MATRIX = ROOT / "evidence" / "IJGGC_V2_R2_FULL_REVIEW_MATRIX.csv"
OUTCOMES = ROOT / "evidence" / "IJGGC_V2_R2_VALIDATION_OUTCOME_PROFILES.csv"
DIMENSIONS = ROOT / "evidence" / "IJGGC_V2_R2_DECISION_EVIDENCE_PROFILES.csv"
TABLE2 = ROOT / "tables" / "ijggc" / "v2_wp8_r2" / "Table02_core_evidence_summary.csv"
TABLE3 = ROOT / "tables" / "ijggc" / "v2_wp8_r2" / "Table03_minimum_validation_packages.csv"
SUPP = ROOT / "supplementary" / "ijggc" / "v2_wp8_r2"
FIGURES = ROOT / "figures" / "ijggc" / "v2_wp8_r2"
TEX = ROOT / "manuscript" / "international-journal-of-greenhouse-gas-control-v2-wp8-r2" / "main.tex"
BIB = TEX.parent / "references_submission_cleaned_v3.bib"
PDF = ROOT / "outputs" / "international_journal_of_greenhouse_gas_control_submission_v2_wp8_r2_major_revision_v1.pdf"
LOG = TEX.parent / "main.log"
PACKAGE = ROOT / "submission" / "international-journal-of-greenhouse-gas-control" / "2026-07-31_v2_wp8_r2_major_revision_v1"

BASE_CORE = ROOT / "evidence" / "IJGGC_V2_HUMAN_REVIEW_SYNCHRONIZED_CORE.csv"
WORKBOOK = (
    ROOT / "outputs" / "ijggc_v2_remaining31_adjudication_2026-07-30"
    / "IJGGC_V2_REMAINING31_ADJUDICATION_WORKBOOK.xlsx"
)
EXPECTED_BASE_SHA = "d351f4cfd97174a365fa76ab9d1916356292c5dd54a49e875146d1bc3f05c9f2"
EXPECTED_WORKBOOK_SHA = "746e47ecffb74aa34fb36158201678045273560515fddfca588206683c7d1592"

EXPECTED_OUTCOMES = {
    "direct_field_validation": 8,
    "controlled_release_ml_validation": 5,
    "explicit_ood_testing": 14,
    "explicit_cross_site_testing": 1,
    "uncertainty_calibration_or_posterior_check": 13,
    "surrogate_error_propagation": 4,
    "any_physical_diagnostic_checked": 23,
}
EXPECTED_SCORES = {
    "field_evidence_score": 8,
    "physical_consistency_score": 42,
    "uncertainty_score": 14,
    "transferability_score": 7,
    "decision_readiness_score": 11,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_text(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))

    required = [BASE_CORE, WORKBOOK, MANIFEST, CORE, MATRIX, OUTCOMES, DIMENSIONS, TABLE2, TABLE3, TEX, BIB, PDF]
    for path in required:
        check(f"exists::{path.relative_to(ROOT)}", path.exists(), "required WP8-R2 artifact")
    if not all(path.exists() for path in required):
        write_report(checks)
        raise SystemExit(1)

    check("locked base core hash", sha256(BASE_CORE) == EXPECTED_BASE_SHA, EXPECTED_BASE_SHA)
    check("remaining31 workbook hash", sha256(WORKBOOK) == EXPECTED_WORKBOOK_SHA, EXPECTED_WORKBOOK_SHA)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("locked core count", manifest.get("locked_core_record_count") == 70, str(manifest.get("locked_core_record_count")))
    check("main quantitative count", manifest.get("main_quantitative_record_count") == 57, str(manifest.get("main_quantitative_record_count")))
    check("full matrix count", manifest.get("full_matrix_item_count") == 627, str(manifest.get("full_matrix_item_count")))
    expected_basis = {
        "independent_exact_agreement_retained": 139,
        "author_adjudicated_disagreement": 450,
        "author_verified_locked_baseline_unavailable": 38,
    }
    check("decision basis counts", manifest.get("decision_basis_counts") == expected_basis, str(manifest.get("decision_basis_counts")))

    core = read_csv(CORE)
    matrix = read_csv(MATRIX)
    main_core = [row for row in core if row.get("wp4_main_claim_eligible", "").lower() == "yes"]
    check("derived core has 70 rows", len(core) == 70, str(len(core)))
    check("derived main universe has 57 rows", len(main_core) == 57, str(len(main_core)))
    check("core paper_id unique", len({row["paper_id"] for row in core}) == 70, "no duplicate paper_id")
    check("matrix is 57 x 11", len(matrix) == 627 and len({(r["paper_id"], r["field"]) for r in matrix}) == 627, str(len(matrix)))
    check("matrix covers 57 papers", len({row["paper_id"] for row in matrix}) == 57, str(len({row["paper_id"] for row in matrix})))
    basis = Counter(row["decision_basis"] for row in matrix)
    check("matrix basis counts", dict(basis) == expected_basis, str(dict(basis)))
    check("no blank final values", all(row.get("final_value", "").strip() for row in matrix), "all 627 final values populated")

    by_id = {row["paper_id"]: row for row in core}
    metadata_expectations = {
        "Zhang2021_LearningInversionFreeForecast": ("Dan Lu", "2022", "Frontiers in Energy Research", "10.3389/fenrg.2021.752185"),
        "Lu2022_BayesianOptimization": ("Xueying Lu", "2022", "Engineering", "10.1016/j.eng.2022.06.011"),
        "ESR_RefNone_173": ("Xinyuan Zou", "2024", "ACS Omega", "10.1021/acsomega.3c07962"),
        "Wen2021_PlumeDNN": ("Gege Wen", "2021", "International Journal of Greenhouse Gas Control", "10.1016/j.ijggc.2020.103223"),
        "Attanasi2025_ResourceML": ("Emil Attanasi", "2025", "Frontiers in Environmental Science", "10.3389/fenvs.2025.1562087"),
        "Crain2023_MonitoringHistory": ("Dylan M. Crain", "2024", "Computational Geosciences", "10.1007/s10596-023-10216-3"),
        "Lin2020_PressureLeakage": ("Saurabh Sinha", "2020", "International Journal of Greenhouse Gas Control", "10.1016/j.ijggc.2020.103189"),
    }
    for paper_id, (author, year, venue, doi) in metadata_expectations.items():
        row = by_id.get(paper_id, {})
        ok = author in row.get("authors", "") and row.get("year") == year and row.get("venue") == venue and doi in row.get("doi_or_url", "")
        if paper_id == "ESR_RefNone_173":
            ok = ok and ".s001" not in row.get("doi_or_url", "")
        check(f"metadata normalized::{paper_id}", ok, f"{author}; {year}; {venue}; {doi}")

    outcomes = {row["outcome"]: int(row["positive_n"]) for row in read_csv(OUTCOMES) if row["application_group"] == "ALL"}
    dimensions = {row["dimension"]: int(row["score_ge3_n"]) for row in read_csv(DIMENSIONS) if row["application_group"] == "ALL"}
    check("validation outcome vector", all(outcomes.get(k) == v for k, v in EXPECTED_OUTCOMES.items()), str(outcomes))
    check("score >=3 vector", dimensions == EXPECTED_SCORES, str(dimensions))

    table2 = read_csv(TABLE2)
    table2_sums = {
        "N": sum(int(row["N"]) for row in table2),
        "field": sum(int(row["field_evaluation"]) for row in table2),
        "controlled": sum(int(row["controlled_event"]) for row in table2),
        "ood": sum(int(row["OOD"]) for row in table2),
        "cross": sum(int(row["cross_site_or_setting"]) for row in table2),
        "uq": sum(int(row["calibrated_UQ_or_posterior"]) for row in table2),
        "physical": sum(int(row["physical_diagnostic"]) for row in table2),
        "surrogate": sum(int(row["surrogate_error_propagation"]) for row in table2),
    }
    check("Table 2 totals", table2_sums == {"N": 57, "field": 8, "controlled": 5, "ood": 14, "cross": 1, "uq": 13, "physical": 23, "surrogate": 4}, str(table2_sums))
    table3 = read_csv(TABLE3)
    package_totals = Counter()
    for row in table3:
        values = dict(re.findall(r"([A-Za-z/-]+)=([0-9]+)", row["current_verified_status"]))
        for key, value in values.items():
            normalized_key = "UQ" if key == "UQ/posterior" else key
            package_totals[normalized_key] += int(value)
    check("Table 3 package totals", package_totals == Counter({"N": 57, "field": 8, "controlled": 5, "OOD": 14, "cross-site": 1, "UQ": 13, "surrogate-error": 4, "physical-diagnostic": 23}), str(dict(package_totals)))

    supp_files = sorted(SUPP.glob("TableS*.csv"))
    expected_supp_names = (
        "TableS01_main_claim_eligible_core.csv", "TableS02_decision_evidence_profiles.csv",
        "TableS03_validation_outcome_profiles.csv", "TableS04_minimum_validation_packages_full.csv",
        "TableS05_field_anchor_summary.csv", "TableS06_figure_traceability.csv",
        "TableS07_master_screening_ledger.csv", "TableS08_decision_application_crosswalk.csv",
        "TableS09_journal_only_sensitivity.csv", "TableS09a_publication_status_normalization.csv",
        "TableS10_update_search_log.csv", "TableS11_independent_review_final_matrix.csv",
        "TableS12_intercoder_agreement.csv", "TableS13_independent_review_summary.csv",
        "TableS14_intercoder_confusion_matrix.csv", "TableS15_intercoder_reliability_diagnostics.csv",
        "TableS16_adjudication_dependence_sensitivity.csv",
    )
    check("Tables S1-S16 exist", len(supp_files) == len(expected_supp_names) and all((SUPP / name).exists() for name in expected_supp_names), f"{len(supp_files)} CSV files")
    s11 = read_csv(SUPP / "TableS11_independent_review_final_matrix.csv")
    s13 = {row["item"]: row["value"] for row in read_csv(SUPP / "TableS13_independent_review_summary.csv")}
    check("Table S11 has 627 items", len(s11) == 627, str(len(s11)))
    check("Table S13 baseline-unavailable = 38", s13.get("baseline_unavailable_items_author_verified") == "38", str(s13.get("baseline_unavailable_items_author_verified")))
    s15 = read_csv(SUPP / "TableS15_intercoder_reliability_diagnostics.csv")
    weighted = [row for row in s15 if row.get("linear_weighted_kappa") and row.get("quadratic_weighted_kappa")]
    check("Table S15 weighted reliability diagnostics", len(weighted) == 5 and all(row.get("linear_weighted_kappa") and row.get("quadratic_weighted_kappa") for row in weighted), f"{len(weighted)} ordered fields")
    s16 = read_csv(SUPP / "TableS16_adjudication_dependence_sensitivity.csv")
    check("Table S16 adjudication-dependence outcomes", len(s16) == 11 and all(int(row["final_positive_n"]) == int(row["positive_exact_agreement_n"]) + int(row["positive_author_adjudicated_n"]) + int(row["positive_baseline_unavailable_verified_n"]) for row in s16), f"{len(s16)} outcomes")
    check("no Wilson intervals in public S2/S3", "wilson" not in (SUPP / "TableS02_decision_evidence_profiles.csv").read_text(encoding="utf-8-sig").lower() and "wilson" not in (SUPP / "TableS03_validation_outcome_profiles.csv").read_text(encoding="utf-8-sig").lower(), "absolute counts and missingness only")
    public_text = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace") for path in supp_files)
    check("no absolute local paths in supplement", "c:/users/" not in public_text.lower() and "c:\\users\\" not in public_text.lower(), "repository-relative/public sources only")
    raw_logs = list((SUPP / "search_update_raw").rglob("*.json"))
    check("raw update-search logs included", len(raw_logs) >= 6, str(len(raw_logs)))
    fig_s1 = ROOT / "figures" / "ijggc" / "v2_wp8" / "supplementary" / "FigS01_record_disposition.pdf"
    check("Figure S1 available", fig_s1.exists(), str(fig_s1.relative_to(ROOT)))
    check("coding manuals available", (ROOT / "evidence" / "JOURNAL_NEUTRAL_CODEBOOK_V1.md").exists() and (ROOT / "evidence" / "COMPETING_REVIEW_DELTA_CODEBOOK.md").exists(), "two codebooks")

    for stem in ("Fig01_decision_chain_evidence_framework", "Fig02_evidence_regimes_by_application", "Fig03_missingness_aware_maturity_dimensions", "Fig04_validation_outcomes_by_application", "Fig05_field_anchor_evidence_roles"):
        for ext in ("pdf", "png", "svg"):
            check(f"figure::{stem}.{ext}", (FIGURES / ext / f"{stem}.{ext}").exists(), "final R2 figure")
    fig3_rows = read_csv(FIGURES / "data" / "Fig03_plot_data.csv")
    fig4 = (FIGURES / "data" / "Fig04_plot_data.csv").read_text(encoding="utf-8-sig")
    fig3_high_grade = Counter()
    for row in fig3_rows:
        if row["category"] in {"Score 3", "Score 4"}:
            fig3_high_grade[row["dimension"]] += int(row["N"])
    check("Figure 3 data synchronized", dict(fig3_high_grade) == EXPECTED_SCORES, str(dict(fig3_high_grade)))
    check("Figure 4 data synchronized", all(str(v) in fig4 for v in EXPECTED_OUTCOMES.values()), "8/5/14/1/13/4/23 present")

    tex = TEX.read_text(encoding="utf-8")
    stale_patterns = ["3 / 3 / 26", "3/2/4/2/2", "6 / 4 / 18", "34.7\\%", "11 full-text", "145 records"]
    check("no stale statistical claims in source", not any(pattern in tex for pattern in stale_patterns), str(stale_patterns))
    check("manuscript states full review", "All 57 papers underwent independent recoding" in tex and "two prespecified batches of 26 and 31 papers" in tex, "full 57-paper review disclosed")
    check(
        "AI declaration synchronized",
        "used OpenAI Codex to assist with language and readability refinement" in tex
        and "candidate consistency flags generated with OpenAI Codex" in tex
        and "were not accepted as final evidence codes" in tex
        and "No generative AI was used to create scientific images or alter figure data" in tex,
        "named tool, disclosed purposes, human verification, and figure boundary",
    )
    check("MRV terminology consistent", "measurement, reporting" not in tex.lower() and "monitoring, reporting and verification" in tex, "MRV = monitoring, reporting and verification")
    check(
        "glossary present",
        all(f"\\textbf{{{term}}}" in tex for term in ("OOD", "UQ", "FNO", "GNN", "THM", "RMSE", "EOR", "QICS", "SACROC", "ZERT")),
        "ten requested abbreviations",
    )
    check("CRediT official role wording", "Writing--original draft" in tex and "Writing--review and editing" in tex, "official CRediT labels")
    check("Figure S1 cited", "Figure S1" in tex, "screening disposition")
    check(
        "GitHub/Zenodo statement is prospective",
        "will be deposited before submission" in tex
        and "No persistent DOI is claimed until" in tex,
        "no inactive DOI claimed",
    )
    check("no nocite packing", "\\nocite" not in tex, "main bibliography contains narrative citations only")

    bib_text = BIB.read_text(encoding="utf-8")
    dois = [value.lower().strip().rstrip(".,") for value in re.findall(r"doi\s*=\s*[\{\"]([^\}\"]+)", bib_text, flags=re.I)]
    duplicate_dois = sorted(doi for doi, count in Counter(dois).items() if count > 1)
    check("no duplicate DOI in bibliography", not duplicate_dois, str(duplicate_dois))
    required_dois = (
        "10.3389/fenrg.2021.752185", "10.1021/acsomega.3c07962", "10.1016/j.eng.2022.06.011",
        "10.1016/j.ijggc.2020.103223", "10.3389/fenvs.2025.1562087",
        "10.1007/s10596-023-10216-3", "10.1016/j.ijggc.2020.103189",
    )
    check("bibliography metadata corrected", all(doi in bib_text for doi in required_dois) and ".s001" not in bib_text and "10.1029/2020WR029123" not in bib_text, "seven verified DOI records and stale Wen DOI removed")

    extracted = pdf_text(PDF)
    check("PDF text has synchronized outcome vector", all(token in extracted for token in ("direct field evaluation was identified in 8", "in 5", "testing in 14", "testing in 1", "checking in 13", "propagation in 4", "diagnostic in 23")), "abstract counts")
    check("PDF has no unresolved markers", not re.search(r"RefNone|ESR_RefNone|information to verify|Unknown authors|\?\?+|9999|citation needed|TODO|TBD", extracted, flags=re.I), "no placeholder text")
    log_text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
    check("LaTeX references resolved", "undefined references" not in log_text.lower() and "undefined citations" not in log_text.lower() and "Label(s) may have changed" not in log_text, "cross-references stable")

    if PACKAGE.exists() and (PACKAGE / "FILE_MANIFEST_SHA256.csv").exists():
        manifest_rows = read_csv(PACKAGE / "FILE_MANIFEST_SHA256.csv")
        package_ok = all((PACKAGE / row["relative_path"]).exists() and sha256(PACKAGE / row["relative_path"]) == row["sha256"] for row in manifest_rows)
        check("package SHA256 manifest", package_ok, f"{len(manifest_rows)} files")
    else:
        check("package SHA256 manifest", False, "package must be rebuilt after final reports")

    write_report(checks)
    failures = [name for name, ok, _ in checks if not ok]
    print(f"WP8-R2 validation: {len(checks) - len(failures)}/{len(checks)} checks passed")
    if failures:
        print("Failures:")
        for name in failures:
            print(f"- {name}")
        raise SystemExit(1)


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    failures = [name for name, ok, _ in checks if not ok]
    lines = [
        "# IJGGC V2 WP8-R2 validation report",
        "",
        f"- Status: **{'PASS' if not failures else 'FAIL'}**",
        f"- Checks passed: {len(checks) - len(failures)}/{len(checks)}",
        "- Quantitative source: full 57-paper independently reviewed and author-adjudicated R2 matrix.",
        "- Locked 70-paper upstream corpus and completed adjudication workbooks were hash-checked and not modified.",
        "",
        "## Checks",
        "",
    ]
    for name, ok, detail in checks:
        lines.append(f"- [{'x' if ok else ' '}] `{name}`: {detail}")
    if failures:
        lines.extend(["", "## Blocking failures", ""] + [f"- {name}" for name in failures])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
